"""
Time acceleration engine for the organizational simulation.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class TimeEngine:
    """Manages accelerated time for the simulation."""
    
    def __init__(self, acceleration_factor: int = 144):
        """
        Initialize the time engine.
        
        Args:
            acceleration_factor: How much to accelerate time (144 = 10 seconds = 1 day)
        """
        self.acceleration_factor = acceleration_factor
        self.real_start_time = datetime.now()
        self.simulation_start_time = datetime.now()
        self.is_running = False
        self._tick_callbacks: list[Callable[[datetime], None]] = []
        self._task: Optional[asyncio.Task] = None
        
    def start(self) -> None:
        """Start the time engine."""
        if self.is_running:
            logger.warning("Time engine is already running")
            return
            
        self.is_running = True
        self.real_start_time = datetime.now()
        self._task = asyncio.create_task(self._time_loop())
        logger.info(f"Time engine started with {self.acceleration_factor}x acceleration")
    
    async def stop(self) -> None:
        """Stop the time engine."""
        if not self.is_running:
            return
            
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Time engine stopped")
    
    def get_current_simulation_time(self) -> datetime:
        """Get the current simulation time."""
        if not self.is_running:
            return self.simulation_start_time
            
        real_elapsed = datetime.now() - self.real_start_time
        simulation_elapsed = real_elapsed * self.acceleration_factor
        return self.simulation_start_time + simulation_elapsed
    
    def real_to_simulation_time(self, real_time: datetime) -> datetime:
        """Convert real time to simulation time."""
        real_elapsed = real_time - self.real_start_time
        simulation_elapsed = real_elapsed * self.acceleration_factor
        return self.simulation_start_time + simulation_elapsed
    
    def simulation_to_real_time(self, simulation_time: datetime) -> datetime:
        """Convert simulation time to real time."""
        simulation_elapsed = simulation_time - self.simulation_start_time
        real_elapsed = simulation_elapsed / self.acceleration_factor
        return self.real_start_time + real_elapsed
    
    def add_tick_callback(self, callback: Callable[[datetime], None]) -> None:
        """Add a callback to be called on each time tick."""
        self._tick_callbacks.append(callback)
    
    def remove_tick_callback(self, callback: Callable[[datetime], None]) -> None:
        """Remove a tick callback."""
        if callback in self._tick_callbacks:
            self._tick_callbacks.remove(callback)
    
    async def _time_loop(self) -> None:
        """Main time loop that triggers callbacks."""
        tick_interval = 1.0  # 1 second real time
        
        try:
            while self.is_running:
                current_sim_time = self.get_current_simulation_time()
                
                # Call all registered callbacks
                for callback in self._tick_callbacks:
                    try:
                        callback(current_sim_time)
                    except Exception as e:
                        logger.error(f"Error in time tick callback: {e}")
                
                await asyncio.sleep(tick_interval)
                
        except asyncio.CancelledError:
            logger.info("Time loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in time loop: {e}")
            self.is_running = False
    
    def get_time_info(self) -> dict:
        """Get information about the current time state."""
        current_sim_time = self.get_current_simulation_time()
        real_elapsed = datetime.now() - self.real_start_time
        sim_elapsed = current_sim_time - self.simulation_start_time
        
        return {
            "is_running": self.is_running,
            "acceleration_factor": self.acceleration_factor,
            "real_start_time": self.real_start_time.isoformat(),
            "simulation_start_time": self.simulation_start_time.isoformat(),
            "current_simulation_time": current_sim_time.isoformat(),
            "real_elapsed_seconds": real_elapsed.total_seconds(),
            "simulation_elapsed_seconds": sim_elapsed.total_seconds(),
            "simulation_days_elapsed": sim_elapsed.total_seconds() / 86400,  # Convert to days
        }


class SimulationScheduler:
    """Schedules events to occur at specific simulation times."""
    
    def __init__(self, time_engine: TimeEngine):
        self.time_engine = time_engine
        self._scheduled_events: list[tuple[datetime, Callable[[], None]]] = []
        self.time_engine.add_tick_callback(self._process_scheduled_events)
    
    def schedule_event(self, simulation_time: datetime, callback: Callable[[], None]) -> None:
        """Schedule an event to occur at a specific simulation time."""
        self._scheduled_events.append((simulation_time, callback))
        # Keep events sorted by time
        self._scheduled_events.sort(key=lambda x: x[0])
        
        logger.debug(f"Scheduled event for {simulation_time}")
    
    def schedule_delay(self, delay_seconds: float, callback: Callable[[], None]) -> None:
        """Schedule an event to occur after a delay in simulation time."""
        current_time = self.time_engine.get_current_simulation_time()
        target_time = current_time + timedelta(seconds=delay_seconds)
        self.schedule_event(target_time, callback)
    
    def schedule_daily_event(self, hour: int, minute: int, callback: Callable[[], None]) -> None:
        """Schedule a recurring daily event at a specific time."""
        current_time = self.time_engine.get_current_simulation_time()
        
        # Find the next occurrence of this time
        target_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time <= current_time:
            target_time += timedelta(days=1)
        
        def recurring_callback():
            callback()
            # Schedule the next occurrence
            next_time = target_time + timedelta(days=1)
            self.schedule_event(next_time, recurring_callback)
        
        self.schedule_event(target_time, recurring_callback)
    
    def _process_scheduled_events(self, current_time: datetime) -> None:
        """Process any scheduled events that should occur now."""
        # Find events that should trigger
        events_to_trigger = []
        remaining_events = []
        
        for event_time, callback in self._scheduled_events:
            if event_time <= current_time:
                events_to_trigger.append(callback)
            else:
                remaining_events.append((event_time, callback))
        
        # Update the scheduled events list
        self._scheduled_events = remaining_events
        
        # Trigger the events
        for callback in events_to_trigger:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error executing scheduled event: {e}")
    
    def get_scheduled_events_info(self) -> list[dict]:
        """Get information about scheduled events."""
        current_time = self.time_engine.get_current_simulation_time()
        
        events_info = []
        for event_time, callback in self._scheduled_events:
            time_until = event_time - current_time
            events_info.append({
                "scheduled_time": event_time.isoformat(),
                "seconds_until": time_until.total_seconds(),
                "callback_name": callback.__name__ if hasattr(callback, '__name__') else str(callback),
            })
        
        return events_info

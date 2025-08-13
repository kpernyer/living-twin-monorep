import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');

// Test configuration
export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate must be below 10%
    errors: ['rate<0.1'],             // Custom error rate must be below 10%
  },
};

// Base URL - will be set by environment variable in CI
const BASE_URL = __ENV.BASE_URL || 'https://living-twin-api-staging-abc123.a.run.app';

// Test data
const testQueries = [
  'What are the main goals for this quarter?',
  'Show me recent documents about project planning',
  'Find information about team performance metrics',
  'What are the key objectives for the development team?',
  'Search for documents related to user feedback',
];

const testDocuments = [
  {
    title: 'Test Document 1',
    content: 'This is a test document for load testing purposes.',
    tags: ['test', 'load-testing'],
  },
  {
    title: 'Test Document 2', 
    content: 'Another test document with different content for variety.',
    tags: ['test', 'performance'],
  },
];

// Helper function to get random item from array
function getRandomItem(array) {
  return array[Math.floor(Math.random() * array.length)];
}

// Main test function
export default function () {
  // Test 1: Health check
  let healthResponse = http.get(`${BASE_URL}/healthz`);
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 100ms': (r) => r.timings.duration < 100,
  }) || errorRate.add(1);

  sleep(1);

  // Test 2: Search query
  let searchQuery = getRandomItem(testQueries);
  let searchPayload = JSON.stringify({
    query: searchQuery,
    tenant_id: 'tenant-test123',
    limit: 10,
  });

  let searchParams = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer test-token', // Mock token for load testing
    },
  };

  let searchResponse = http.post(`${BASE_URL}/search`, searchPayload, searchParams);
  check(searchResponse, {
    'search status is 200 or 401': (r) => r.status === 200 || r.status === 401, // 401 expected without real auth
    'search response time < 2000ms': (r) => r.timings.duration < 2000,
    'search response has data structure': (r) => {
      try {
        let body = JSON.parse(r.body);
        return body.hasOwnProperty('success');
      } catch (e) {
        return false;
      }
    },
  }) || errorRate.add(1);

  sleep(1);

  // Test 3: Document ingestion endpoint (should fail without auth, but tests the endpoint)
  let docPayload = JSON.stringify(getRandomItem(testDocuments));
  let ingestResponse = http.post(`${BASE_URL}/ingest/text`, docPayload, searchParams);
  check(ingestResponse, {
    'ingest endpoint responds': (r) => r.status >= 200 && r.status < 500,
    'ingest response time < 1000ms': (r) => r.timings.duration < 1000,
  }) || errorRate.add(1);

  sleep(1);

  // Test 4: Goals endpoint
  let goalsResponse = http.get(`${BASE_URL}/goals`, searchParams);
  check(goalsResponse, {
    'goals endpoint responds': (r) => r.status >= 200 && r.status < 500,
    'goals response time < 1000ms': (r) => r.timings.duration < 1000,
  }) || errorRate.add(1);

  sleep(1);

  // Test 5: Users endpoint
  let usersResponse = http.get(`${BASE_URL}/users`, searchParams);
  check(usersResponse, {
    'users endpoint responds': (r) => r.status >= 200 && r.status < 500,
    'users response time < 1000ms': (r) => r.timings.duration < 1000,
  }) || errorRate.add(1);

  // Random sleep between 1-3 seconds to simulate real user behavior
  sleep(Math.random() * 2 + 1);
}

// Setup function - runs once before the test
export function setup() {
  console.log(`Starting load test against: ${BASE_URL}`);
  
  // Verify the service is accessible
  let response = http.get(`${BASE_URL}/healthz`);
  if (response.status !== 200) {
    throw new Error(`Service not accessible. Health check failed with status: ${response.status}`);
  }
  
  console.log('Service is accessible. Starting load test...');
  return { baseUrl: BASE_URL };
}

// Teardown function - runs once after the test
export function teardown(data) {
  console.log('Load test completed');
  console.log(`Tested against: ${data.baseUrl}`);
}

import { createContext, useContext, useEffect, useState } from 'react'
import { onAuthStateChanged, signOut, signInWithEmailAndPassword, createUserWithEmailAndPassword, signInWithPopup, GoogleAuthProvider, signInAnonymously } from 'firebase/auth'
import { auth } from '../../shared/firebase.ts'

const AuthContext = createContext({})

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Mock AprioOne service for organization management
class AprioOneService {
  static async checkEmailDomainOrganization(email) {
    const domain = email.split('@')[1]?.toLowerCase()
    
    // Mock API call to AprioOne system
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Mock registered domains
    const registeredDomains = {
      'acme.com': {
        id: 'aprio_org_acme',
        name: 'Acme Corporation',
        webUrl: 'https://acme.com',
        industry: 'Technology',
        size: '201-1000 employees',
        techContact: 'tech@acme.com',
        businessContact: 'hr@acme.com',
        adminPortalUrl: 'https://admin.acme.aprioone.com',
        status: 'active',
        features: ['chat', 'pulse', 'ingest', 'analytics'],
        branding: {
          primaryColor: '#1976D2',
          logo: 'https://acme.com/logo.png',
          theme: 'corporate'
        },
        emailDomains: ['acme.com'],
        autoBindNewUsers: true,
      },
      'techcorp.io': {
        id: 'aprio_org_techcorp',
        name: 'TechCorp Solutions',
        webUrl: 'https://techcorp.io',
        industry: 'Software',
        size: '51-200 employees',
        techContact: 'admin@techcorp.io',
        businessContact: 'hr@techcorp.io',
        adminPortalUrl: 'https://admin.techcorp.aprioone.com',
        status: 'active',
        features: ['chat', 'pulse', 'ingest'],
        branding: {
          primaryColor: '#4CAF50',
          logo: 'https://techcorp.io/logo.png',
          theme: 'modern'
        },
        emailDomains: ['techcorp.io'],
        autoBindNewUsers: true,
      }
    }
    
    return registeredDomains[domain] || null
  }

  static async validateInvitationCode(invitationCode) {
    if (!invitationCode.startsWith('APRIO-') || invitationCode.length < 15) {
      throw new Error('Invalid invitation code format. Please check with your organization admin.')
    }

    // Mock API call to AprioOne system
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const parts = invitationCode.split('-')
    if (parts.length < 3) {
      throw new Error('Invalid invitation code format')
    }
    
    const orgCode = parts[1]
    const inviteId = parts[2]
    
    // Mock organization data from AprioOne system
    return {
      organization: {
        id: `aprio_org_${orgCode.toLowerCase()}`,
        name: 'Acme Corporation',
        webUrl: 'https://acme.com',
        industry: 'Technology',
        size: '201-1000 employees',
        techContact: 'tech@acme.com',
        businessContact: 'hr@acme.com',
        adminPortalUrl: 'https://admin.acme.aprioone.com',
        createdBy: 'aprioone_admin',
        status: 'active',
        features: ['chat', 'pulse', 'ingest', 'analytics'],
        branding: {
          primaryColor: '#1976D2',
          logo: 'https://acme.com/logo.png',
          theme: 'corporate'
        }
      },
      userRole: 'employee',
      department: 'Engineering',
      permissions: ['read', 'write'],
      inviteId
    }
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [organization, setOrganization] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // Check if user has organization binding
        const orgData = localStorage.getItem(`org_${firebaseUser.uid}`)
        if (orgData) {
          setOrganization(JSON.parse(orgData))
        } else {
          // Check email domain for automatic organization binding
          try {
            const org = await AprioOneService.checkEmailDomainOrganization(firebaseUser.email)
            if (org) {
              setOrganization(org)
              localStorage.setItem(`org_${firebaseUser.uid}`, JSON.stringify(org))
            }
          } catch (error) {
            console.error('Error checking organization:', error)
          }
        }
      } else {
        setOrganization(null)
      }
      
      setUser(firebaseUser)
      setLoading(false)
    })

    return unsubscribe
  }, [])

  const signInWithEmail = async (email, password) => {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password)
      
      // Check for organization binding
      const org = await AprioOneService.checkEmailDomainOrganization(email)
      if (org) {
        setOrganization(org)
        localStorage.setItem(`org_${result.user.uid}`, JSON.stringify(org))
      }
      
      return { success: true, user: result.user, organization: org }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const signUpWithEmail = async (email, password) => {
    try {
      const result = await createUserWithEmailAndPassword(auth, email, password)
      
      // Check for organization binding
      const org = await AprioOneService.checkEmailDomainOrganization(email)
      if (org) {
        setOrganization(org)
        localStorage.setItem(`org_${result.user.uid}`, JSON.stringify(org))
      }
      
      return { success: true, user: result.user, organization: org }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const signInWithGoogle = async () => {
    try {
      const provider = new GoogleAuthProvider()
      const result = await signInWithPopup(auth, provider)
      
      // Check for organization binding
      const org = await AprioOneService.checkEmailDomainOrganization(result.user.email)
      if (org) {
        setOrganization(org)
        localStorage.setItem(`org_${result.user.uid}`, JSON.stringify(org))
      }
      
      return { success: true, user: result.user, organization: org }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const signInAsGuest = async () => {
    try {
      const result = await signInAnonymously(auth)
      return { success: true, user: result.user }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const acceptInvitation = async (invitationCode) => {
    try {
      const inviteData = await AprioOneService.validateInvitationCode(invitationCode)
      
      // For invitation flow, we create an anonymous user first, then bind to organization
      const result = await signInAnonymously(auth)
      
      // Bind user to organization
      setOrganization(inviteData.organization)
      localStorage.setItem(`org_${result.user.uid}`, JSON.stringify(inviteData.organization))
      localStorage.setItem(`invite_${result.user.uid}`, JSON.stringify({
        invitationCode,
        role: inviteData.userRole,
        department: inviteData.department,
        permissions: inviteData.permissions,
        inviteId: inviteData.inviteId
      }))
      
      return { 
        success: true, 
        user: result.user, 
        organization: inviteData.organization,
        message: `Successfully joined ${inviteData.organization.name}!`
      }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const logout = async () => {
    try {
      if (user) {
        localStorage.removeItem(`org_${user.uid}`)
        localStorage.removeItem(`invite_${user.uid}`)
      }
      await signOut(auth)
      setOrganization(null)
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  const getUserRole = () => {
    if (!user) return null
    
    const inviteData = localStorage.getItem(`invite_${user.uid}`)
    if (inviteData) {
      const data = JSON.parse(inviteData)
      return data.role
    }
    
    // Default role for email domain binding
    return organization ? 'employee' : 'user'
  }

  const getUserPermissions = () => {
    if (!user) return []
    
    const inviteData = localStorage.getItem(`invite_${user.uid}`)
    if (inviteData) {
      const data = JSON.parse(inviteData)
      return data.permissions
    }
    
    // Default permissions for email domain binding
    return organization ? ['read', 'write'] : ['read']
  }

  const isOrganizationAdmin = () => {
    const permissions = getUserPermissions()
    return permissions.includes('admin')
  }

  const getTenantId = () => {
    return organization?.id || 'demo'
  }

  const value = {
    user,
    organization,
    loading,
    logout,
    signInWithEmail,
    signUpWithEmail,
    signInWithGoogle,
    signInAsGuest,
    acceptInvitation,
    getUserRole,
    getUserPermissions,
    isOrganizationAdmin,
    getTenantId,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

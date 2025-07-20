import { Clerk } from '@clerk/clerk-js'

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

console.log('Clerk key:', clerkPubKey) // Debug log

// Show loading message while Clerk initializes
document.getElementById('app').innerHTML = `
  <div style="text-align: center; padding: 50px;">
    <h2>Loading...</h2>
  </div>
`

try {
  const clerk = new Clerk(clerkPubKey)
  await clerk.load()

  if (clerk.user) {
    document.getElementById('app').innerHTML = `
      <div style="text-align: center; padding: 50px;">
        <h2>Welcome back!</h2>
        <div id="user-button"></div>
      </div>
    `

    const userButtonDiv = document.getElementById('user-button')
    clerk.mountUserButton(userButtonDiv)
  } else {
    document.getElementById('app').innerHTML = `
      <div style="text-align: center; padding: 50px;">
        <h2>Please Sign In</h2>
        <div id="sign-in"></div>
      </div>
    `

    const signInDiv = document.getElementById('sign-in')
    clerk.mountSignIn(signInDiv)
  }
} catch (error) {
  console.error('Clerk initialization error:', error)
  document.getElementById('app').innerHTML = `
    <div style="text-align: center; padding: 50px; color: red;">
      <h2>Error loading authentication</h2>
      <p>Please check your Clerk configuration.</p>
      <p>Error: ${error.message}</p>
    </div>
  `
}

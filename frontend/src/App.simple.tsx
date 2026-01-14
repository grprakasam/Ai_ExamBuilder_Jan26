function App() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      fontFamily: 'sans-serif'
    }}>
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '20px' }}>EOG Prep Pro</h1>
        <p style={{ fontSize: '1.5rem', marginBottom: '30px' }}>Application is loading...</p>
        <p style={{ fontSize: '1rem', opacity: 0.8 }}>If you see this message, React is working!</p>
      </div>
    </div>
  )
}

export default App

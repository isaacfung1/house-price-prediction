import { useState } from 'react'
import './App.css'

function App() {
  const [beds, setBeds] = useState(3)
  const [baths, setBaths] = useState(2)
  const [sqft, setSqft] = useState(1500)
  const [price, setPrice] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [details, setDetails] = useState(null)

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    setPrice(null);

    try {
      // 1. Prepare Payload (Hardcoded location for now)
      const payload = {
        latitude: 44.0,
        longitude: -79.46,
        bedrooms: parseInt(beds)
      };

      // 2. Call API
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error("API Connection Failed");

      const data = await response.json();
      
      // 3. Format Currency
      const formattedPrice = new Intl.NumberFormat('en-CA', { 
        style: 'currency', currency: 'CAD', maximumFractionDigits: 0 
      }).format(data.estimated_price);

      setPrice(formattedPrice);
      setDetails(data.location_info.address);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h2>🏡 Price AI</h2>
      
      <div className="input-group">
        <label>Bedrooms</label>
        <input 
          type="number" 
          value={beds} 
          onChange={(e) => setBeds(e.target.value)}
        />
      </div>

      <div className="input-group">
        <label>Bathrooms</label>
        <input type="number" 
        value={baths} 
        onChange={(e) => setBaths(e.target.value)}/>
      </div>

      <div className="input-group">
        <label>Square Footage</label>
        <input 
          type="number"
          value={sqft} 
          onChange={(e) => setSqft(e.target.value)}
        />
      </div>

      <button onClick={handlePredict} disabled={loading}>
        {loading ? "Calculating..." : "Get Price"}
      </button>

      {error && <p className="error">{error}</p>}
      
      {price && (
        <div className="result">
          <h3>{price}</h3>
          <p className="small">{details}</p>
        </div>
      )}
    </div>
  )
}

export default App
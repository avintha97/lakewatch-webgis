import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LakeAreaCalculator.css';

const LakeAreaCalculator = () => {
  const navigate = useNavigate();
  const [bbox, setBbox] = useState([
    [81.39865413309057, 7.099820828875569],
    [81.55658259988745, 7.099820828875569],
    [81.55658259988745, 7.281713154976799],
    [81.39865413309057, 7.281713154976799],
    [81.39865413309057, 7.099820828875569],
  ]);
  
  const [date, setDate] = useState('2025-01-27');
  const [threshold, setThreshold] = useState(-17);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        bbox: bbox,
        date: date,
        vv_vh_threshold: threshold,
      };

      const response = await fetch('http://127.0.0.1:5000/api/v1/lakes/area', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBboxChange = (index, coordIndex, value) => {
    const newBbox = [...bbox];
    newBbox[index][coordIndex] = parseFloat(value);
    setBbox(newBbox);
  };

  const handleNavigateToMap = () => {
    navigate('/map');
  };

  return (
    <div className="lake-calculator">
      <h1>🌊 LakeWatch - Water Area Calculator</h1>
      
      <div className="navigation-bar">
        <button 
          type="button"
          onClick={handleNavigateToMap}
          className="nav-btn primary"
          title="Use interactive map to draw polygons"
        >
          🗺️ Go to Interactive Map
        </button>
      </div>
      
      <form onSubmit={handleSubmit} className="calculator-form">
        {/* Date Input */}
        <div className="form-group">
          <label htmlFor="date">Target Date (±5 days)</label>
          <input
            id="date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>

        {/* Threshold Input */}
        <div className="form-group">
          <label htmlFor="threshold">VV/VH Threshold (dB)</label>
          <input
            id="threshold"
            type="number"
            value={threshold}
            onChange={(e) => setThreshold(parseInt(e.target.value))}
            step="1"
          />
          <small>Lower values = stricter water detection (default: -17)</small>
        </div>

        {/* Bounding Box Inputs */}
        <div className="form-group">
          <label>Bounding Box Coordinates (closed polygon)</label>
          <div className="bbox-container">
            {bbox.map((coord, index) => (
              <div key={index} className="bbox-point">
                <input
                  type="number"
                  placeholder="Longitude"
                  value={coord[0]}
                  onChange={(e) => handleBboxChange(index, 0, e.target.value)}
                  step="0.0001"
                />
                <input
                  type="number"
                  placeholder="Latitude"
                  value={coord[1]}
                  onChange={(e) => handleBboxChange(index, 1, e.target.value)}
                  step="0.0001"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? '⏳ Calculating...' : '📊 Calculate Water Area'}
        </button>
      </form>

      {/* Error Display */}
      {error && (
        <div className="error-box">
          <strong>❌ Error:</strong> {error}
        </div>
      )}

      {/* Result Display */}
      {result && (
        <div className="result-box">
          <h2>📈 Results</h2>
          <table>
            <tbody>
              <tr>
                <td><strong>Target Date:</strong></td>
                <td>{result.target_date}</td>
              </tr>
              <tr>
                <td><strong>Date Range:</strong></td>
                <td>{result.start_date} to {result.end_date}</td>
              </tr>
              <tr>
                <td><strong>Water Area:</strong></td>
                <td className="highlight">{result.water_area_km2} km²</td>
              </tr>
              <tr>
                <td><strong>Pixel Count:</strong></td>
                <td>{result.pixel_count.toLocaleString()}</td>
              </tr>
              <tr>
                <td><strong>Threshold (VV-VH):</strong></td>
                <td>{result.vv_vh_threshold_db} dB</td>
              </tr>
              <tr>
                <td><strong>Satellite:</strong></td>
                <td>{result.satellite}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default LakeAreaCalculator;

import React, { useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, useMap, FeatureGroup } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import '../styles/MapPage.css';

// Fix for default Leaflet markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

/**
 * MapPage: Full Leaflet-based map with polygon drawing, analysis, and results display
 * 
 * Features:
 * - Interactive map centered on Sri Lanka
 * - Draw/Edit/Delete polygon tools
 * - Modal form for analysis parameters
 * - Results panel with data persistence
 * - Integration with backend analysis API
 */
const MapPage = () => {
  // State for polygon and drawing
  const [drawnGeometry, setDrawnGeometry] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [results, setResults] = useState(null);
  const [savedAnalyses, setSavedAnalyses] = useState([]);
  
  // Form state
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    threshold: -17,
    notes: '',
  });
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [showAnalysisHistory, setShowAnalysisHistory] = useState(false);
  
  const featureGroupRef = useRef();

  // Fetch saved analyses on component mount
  useEffect(() => {
    fetchSavedAnalyses();
  }, []);

  /**
   * Convert drawn layer to GeoJSON coordinates (closed polygon)
   */
  const layerToCoordinates = (layer) => {
    if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
      const coords = layer.getLatLngs()[0]; // Get outer ring
      const polygon = coords.map(latlng => [latlng.lng, latlng.lat]);
      
      // Ensure polygon is closed (first point === last point)
      if (JSON.stringify(polygon[0]) !== JSON.stringify(polygon[polygon.length - 1])) {
        polygon.push(polygon[0]);
      }
      return polygon;
    }
    return null;
  };

  /**
   * Handle when a shape is created or edited
   */
  const handleCreated = (e) => {
    const { layer } = e;
    const coordinates = layerToCoordinates(layer);
    
    if (coordinates && coordinates.length >= 4) {
      setDrawnGeometry({
        type: 'Polygon',
        coordinates: [coordinates],
      });
      setShowModal(true);
      setError(null);
    } else {
      setError('Please draw a valid polygon (at least 3 points)');
    }
  };

  /**
   * Handle when a shape is edited
   */
  const handleEdited = (e) => {
    const layers = e.layers;
    layers.eachLayer((layer) => {
      const coordinates = layerToCoordinates(layer);
      if (coordinates) {
        setDrawnGeometry({
          type: 'Polygon',
          coordinates: [coordinates],
        });
      }
    });
  };

  /**
   * Handle shape deletion
   */
  const handleDeleted = (e) => {
    if (featureGroupRef.current && featureGroupRef.current.getLayers().length === 0) {
      setDrawnGeometry(null);
      setShowModal(false);
      setResults(null);
      setShowResults(false);
    }
  };

  /**
   * Fetch list of saved analyses from backend
   */
  const fetchSavedAnalyses = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/v1/analysis/list', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSavedAnalyses(data.analyses || []);
      } else {
        console.warn(`Failed to fetch analyses: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      console.error('Error fetching saved analyses - Backend may not be running:', err);
      setError('Cannot connect to backend. Make sure Flask server is running on http://127.0.0.1:5000');
    }
  };

  /**
   * Calculate water area and save to database
   */
  const handleSubmitAnalysis = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Extract coordinates from GeoJSON
      const coords = drawnGeometry.coordinates[0];
      
      // Step 1: Calculate water area
      const analysisPayload = {
        bbox: coords,
        date: formData.date,
        vv_vh_threshold: parseInt(formData.threshold),
      };

      const analysisResponse = await fetch('http://127.0.0.1:5000/api/v1/lakes/area', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analysisPayload),
      });

      if (!analysisResponse.ok) {
        throw new Error(`Analysis failed: ${analysisResponse.statusText}`);
      }

      const analysisResult = await analysisResponse.json();

      // Step 2: Save to database
      const today = new Date().toISOString().split('T')[0];
      const savePayload = {
        geometry: drawnGeometry,
        date: formData.date,
        threshold: parseInt(formData.threshold),
        water_area_km2: analysisResult.water_area_km2,
        pixel_count: analysisResult.pixel_count,
        submission_date: today,
        satellite: analysisResult.satellite,
        notes: formData.notes,
        analysis_result: analysisResult,
      };

      const saveResponse = await fetch('http://127.0.0.1:5000/api/v1/analysis/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(savePayload),
      });

      if (!saveResponse.ok) {
        throw new Error(`Save failed: ${saveResponse.statusText}`);
      }

      const savedRecord = await saveResponse.json();
      
      // Combine analysis and saved record data
      setResults({
        ...analysisResult,
        recordId: savedRecord.id,
        submissionDate: today,
      });
      
      setShowResults(true);
      setShowModal(false);
      
      // Refresh saved analyses list
      fetchSavedAnalyses();
    } catch (err) {
      setError(`Error: ${err.message}`);
      console.error('Submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Clear drawing and results
   */
  const handleClearAll = () => {
    if (featureGroupRef.current) {
      featureGroupRef.current.clearLayers();
    }
    setDrawnGeometry(null);
    setShowModal(false);
    setResults(null);
    setShowResults(false);
    setError(null);
  };

  /**
   * Close modal without clearing drawing
   */
  const handleCloseModal = () => {
    setShowModal(false);
  };

  return (
    <div className="map-page">
      {/* Header */}
      <header className="map-header">
        <h1>🗺️ LakeWatch Interactive Map</h1>
        <p>Draw a polygon on the map to analyze water area</p>
      </header>

      {/* Controls Bar */}
      <div className="controls-bar">
        <button 
          onClick={handleClearAll} 
          className="btn btn-danger"
          title="Clear all drawings and results"
        >
          🗑️ Clear All
        </button>
        <button 
          onClick={() => setShowAnalysisHistory(!showAnalysisHistory)} 
          className="btn btn-info"
          title="View saved analyses"
        >
          📋 Analysis History ({savedAnalyses.length})
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <strong>❌ Error:</strong> {error}
          <button onClick={() => setError(null)} className="close-btn">&times;</button>
        </div>
      )}

      {/* Main Content */}
      <div className="map-container-wrapper">
        {/* Map */}
        <MapContainer 
          center={[7.8, 80.8]} 
          zoom={8} 
          className="map-container"
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
          />
          <FeatureGroup ref={featureGroupRef}>
            <EditControl
              position="topleft"
              onCreated={handleCreated}
              onEdited={handleEdited}
              onDeleted={handleDeleted}
              draw={{
                rectangle: true,
                polygon: true,
                polyline: false,
                circle: false,
                marker: false,
                circlemarker: false,
              }}
            />
          </FeatureGroup>
        </MapContainer>

        {/* Results Panel */}
        {showResults && results && (
          <div className="results-panel">
            <h3>📊 Analysis Results</h3>
            <div className="result-item">
              <span className="label">Record ID:</span>
              <span className="value">{results.recordId}</span>
            </div>
            <div className="result-item">
              <span className="label">Water Area:</span>
              <span className="value highlight">{results.water_area_km2} km²</span>
            </div>
            <div className="result-item">
              <span className="label">Pixels:</span>
              <span className="value">{results.pixel_count.toLocaleString()}</span>
            </div>
            <div className="result-item">
              <span className="label">Date Range:</span>
              <span className="value">{results.start_date} to {results.end_date}</span>
            </div>
            <div className="result-item">
              <span className="label">Threshold:</span>
              <span className="value">{results.vv_vh_threshold_db} dB</span>
            </div>
            <div className="result-item">
              <span className="label">Satellite:</span>
              <span className="value">{results.satellite}</span>
            </div>
            <div className="result-item">
              <span className="label">Submitted:</span>
              <span className="value">{results.submissionDate} {new Date().toLocaleTimeString()}</span>
            </div>
            <button onClick={handleClearAll} className="btn btn-secondary">
              ✨ New Analysis
            </button>
          </div>
        )}
      </div>

      {/* Modal Form */}
      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>⚙️ Analysis Parameters</h2>
              <button 
                className="close-btn" 
                onClick={handleCloseModal}
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleSubmitAnalysis} className="analysis-form">
              {/* Date Input */}
              <div className="form-group">
                <label htmlFor="date">Target Date (±5 days)</label>
                <input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({...formData, date: e.target.value})}
                  required
                />
                <small>Satellites search ±5 days from this date</small>
              </div>

              {/* Threshold Input */}
              <div className="form-group">
                <label htmlFor="threshold">VV/VH Threshold (dB)</label>
                <input
                  id="threshold"
                  type="number"
                  value={formData.threshold}
                  onChange={(e) => setFormData({...formData, threshold: e.target.value})}
                  step="1"
                  required
                />
                <small>Lower values = stricter water detection. Default: -17 dB</small>
              </div>

              {/* Notes Input */}
              <div className="form-group">
                <label htmlFor="notes">Notes (optional)</label>
                <textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  placeholder="Add any observations or notes about this analysis..."
                  rows="3"
                />
              </div>

              {/* Buttons */}
              <div className="modal-actions">
                <button 
                  type="button" 
                  onClick={handleCloseModal}
                  className="btn btn-secondary"
                  disabled={loading}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? '⏳ Analyzing...' : '🔍 Analyze & Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Analysis History Sidebar */}
      {showAnalysisHistory && (
        <div className="history-sidebar">
          <div className="history-header">
            <h3>📋 Analysis History</h3>
            <button 
              className="close-btn"
              onClick={() => setShowAnalysisHistory(false)}
            >
              &times;
            </button>
          </div>
          <div className="history-list">
            {savedAnalyses.length === 0 ? (
              <p className="empty-message">No analyses saved yet</p>
            ) : (
              savedAnalyses.map((analysis) => (
                <div key={analysis.id} className="history-item">
                  <div className="history-date">{analysis.date}</div>
                  <div className="history-area">{analysis.water_area_km2} km²</div>
                  <div className="history-meta">
                    ID: {analysis.id} | {analysis.satellite}
                  </div>
                  {analysis.notes && (
                    <div className="history-notes">{analysis.notes}</div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MapPage;

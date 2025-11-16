import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Home.css';

const Home = () => {
  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1>🌊 LakeWatch WebGIS</h1>
          <p className="subtitle">Real-time Water Area Analysis using Satellite Imagery</p>
          <p className="description">
            Monitor and analyze lake water areas using Sentinel-1 SAR satellite data with precision and ease.
          </p>
          <Link to="/calculator" className="cta-button">
            📊 Calculate Water Area
          </Link>
        </div>
        <div className="hero-image">
          <div className="satellite-icon">🛰️</div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2>✨ Key Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🗺️</div>
            <h3>Custom Geometry</h3>
            <p>Define any lake boundary with precise coordinates</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📡</div>
            <h3>Sentinel-1 SAR</h3>
            <p>Advanced synthetic aperture radar for all-weather analysis</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📅</div>
            <h3>Date Range</h3>
            <p>Analyze water levels with ±5 day flexibility</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Area Calculation</h3>
            <p>Get precise water area in km² with pixel accuracy</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚙️</div>
            <h3>Adjustable Threshold</h3>
            <p>Fine-tune VV/VH threshold for optimal detection</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💾</div>
            <h3>Data Export</h3>
            <p>Save results for reporting and analysis</p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works">
        <h2>🔧 How It Works</h2>
        <div className="steps">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Define Area</h3>
            <p>Input lake coordinates as a closed polygon</p>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <h3>Select Date</h3>
            <p>Choose target date (±5 day range searched)</p>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <h3>Process</h3>
            <p>Sentinel-1 imagery processed and analyzed</p>
          </div>
          <div className="step">
            <div className="step-number">4</div>
            <h3>Results</h3>
            <p>Get water area, pixel count, and metadata</p>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="about">
        <h2>ℹ️ About LakeWatch</h2>
        <div className="about-content">
          <p>
            LakeWatch is a <strong>web-based GIS platform</strong> designed for monitoring and analyzing 
            lake water areas using satellite imagery. Leveraging <strong>Google Earth Engine</strong> and 
            <strong> Sentinel-1 SAR data</strong>, LakeWatch provides accurate, near real-time water 
            surface area measurements.
          </p>
          <p>
            Perfect for <strong>environmental monitoring</strong>, <strong>water resource management</strong>, 
            and <strong>climate research</strong>.
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <h2>Ready to Analyze Your Lake?</h2>
        <Link to="/calculator" className="cta-button-large">
          🚀 Get Started Now
        </Link>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>&copy; 2025 LakeWatch WebGIS. Powered by Google Earth Engine &amp; Sentinel-1 SAR.</p>
      </footer>
    </div>
  );
};

export default Home;

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './index.css';

import Market from './pages/Market';
import ItemPage from './pages/ItemPage';
import Notification from './pages/Notification'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Router>
      <Routes>
          <Route path='/' element={<Market />} />
          <Route path='/market' element={<Market />} />
          <Route path="/item" element={<ItemPage />} />
          <Route path="/notification" element={<Notification />} />
      </Routes>
    </Router>
  </StrictMode>
)

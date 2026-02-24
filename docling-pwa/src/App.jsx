import { Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import CataloguePage from './pages/CataloguePage'
import ScanPage from './pages/ScanPage'
import ValidationPage from './pages/ValidationPage'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 pb-20"> {/* pb-20 pour éviter que la navbar cache le contenu */}
      <main className="max-w-screen-md mx-auto min-h-full">
        <Routes>
          <Route path="/" element={<Navigate to="/scan" replace />} />
          <Route path="/scan" element={<ScanPage />} />
          <Route path="/validation" element={<ValidationPage />} />
          <Route path="/catalogue" element={<CataloguePage />} />
        </Routes>
      </main>
      <Navbar />
    </div>
  )
}

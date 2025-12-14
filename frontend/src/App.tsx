import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import MainLayout from './layouts/MainLayout'
import NewProjectPage from './pages/NewProjectPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import OptimizationRunPage from './pages/OptimizationRunPage'
import DocsPage from './pages/DocsPage'
import RFAnalysisPage from './pages/RFAnalysisPage'
import PerformanceDashboardPage from './pages/PerformanceDashboardPage'
import RFAnalysisToolsPage from './pages/RFAnalysisToolsPage'
import PerformanceMetricsPage from './pages/PerformanceMetricsPage'
import TutorialsPage from './pages/TutorialsPage'
import BestPracticesPage from './pages/BestPracticesPage'
import CaseStudiesPage from './pages/CaseStudiesPage'
import HelpCenterPage from './pages/HelpCenterPage'
import APIDocsPage from './pages/APIDocsPage'
import ContactPage from './pages/ContactPage'
import BugReportsPage from './pages/BugReportsPage'
import AboutPage from './pages/AboutPage'
import FeaturesPage from './pages/FeaturesPage'
import TechnologyPage from './pages/TechnologyPage'
import LicensePage from './pages/LicensePage'
import LegalPage from './pages/LegalPage'
import PrivacyPage from './pages/PrivacyPage'
import TermsPage from './pages/TermsPage'
import CookiesPage from './pages/CookiesPage'

function App() {
  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="projects/new" element={<NewProjectPage />} />
          <Route path="projects/:id" element={<ProjectDetailPage />} />
          <Route path="projects/:id/analysis" element={<RFAnalysisPage />} />
          <Route path="projects/:id/performance" element={<PerformanceDashboardPage />} />
          <Route path="runs/:runId" element={<OptimizationRunPage />} />
          <Route path="docs" element={<DocsPage />} />
          
          {/* Products */}
          <Route path="rf-analysis-tools" element={<RFAnalysisToolsPage />} />
          <Route path="performance-metrics" element={<PerformanceMetricsPage />} />
          
          {/* Learn */}
          <Route path="tutorials" element={<TutorialsPage />} />
          <Route path="best-practices" element={<BestPracticesPage />} />
          <Route path="case-studies" element={<CaseStudiesPage />} />
          
          {/* Support */}
          <Route path="help" element={<HelpCenterPage />} />
          <Route path="api-docs" element={<APIDocsPage />} />
          <Route path="contact" element={<ContactPage />} />
          <Route path="bug-reports" element={<BugReportsPage />} />
          
          {/* About */}
          <Route path="about" element={<AboutPage />} />
          <Route path="features" element={<FeaturesPage />} />
          <Route path="technology" element={<TechnologyPage />} />
          <Route path="license" element={<LicensePage />} />
          
          {/* Legal */}
          <Route path="legal" element={<LegalPage />} />
          <Route path="privacy" element={<PrivacyPage />} />
          <Route path="terms" element={<TermsPage />} />
          <Route path="cookies" element={<CookiesPage />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App

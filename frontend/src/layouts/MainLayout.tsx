import { Outlet, Link, useLocation } from 'react-router-dom'

export default function MainLayout() {
  const location = useLocation()
  const isDashboard = location.pathname === '/'

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'linear-gradient(to bottom right, #f5f6f5 0%, rgba(196, 200, 176, 0.2) 50%, rgba(155, 168, 155, 0.1) 100%)' }}>
      {/* Navigation - Professional Industrial Design */}
      <nav className="bg-white border-b border-neutral-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center group">
                <img 
                  src="/LOGO2.png" 
                  alt="ANTEX Logo" 
                  className="h-10 w-auto object-contain group-hover:opacity-80 transition-opacity duration-200"
                  style={{ maxHeight: '40px' }}
                />
              </Link>
            </div>

            {/* Navigation Links - Professional Style */}
            <div className="hidden md:flex items-center space-x-1">
              <Link 
                to="/" 
                className={`relative px-6 py-3 text-sm font-semibold tracking-wide uppercase transition-all duration-200 ${
                  location.pathname === '/' 
                    ? 'text-primary-dark' 
                    : 'text-neutral-600 hover:text-primary-dark'
                }`}
              >
                Dashboard
                {location.pathname === '/' && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-dark"></span>
                )}
              </Link>
              
              <div className="h-6 w-px bg-neutral-300 mx-2"></div>
              
              <Link 
                to="/projects/new" 
                className={`relative px-6 py-3 text-sm font-semibold tracking-wide uppercase transition-all duration-200 ${
                  location.pathname === '/projects/new' 
                    ? 'text-primary-dark' 
                    : 'text-neutral-600 hover:text-primary-dark'
                }`}
              >
                New Project
                {location.pathname === '/projects/new' && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-dark"></span>
                )}
              </Link>
              
              <div className="h-6 w-px bg-neutral-300 mx-2"></div>
              
              <Link 
                to="/docs" 
                className={`relative px-6 py-3 text-sm font-semibold tracking-wide uppercase transition-all duration-200 ${
                  location.pathname === '/docs' 
                    ? 'text-primary-dark' 
                    : 'text-neutral-600 hover:text-primary-dark'
                }`}
              >
                Documentation
                {location.pathname === '/docs' && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-dark"></span>
                )}
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button className="text-neutral-600 hover:text-primary-dark">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 flex-grow">
        <Outlet />
      </main>

      {/* Conditional Footer: Full footer for dashboard, compact for other pages */}
      {isDashboard ? (
        /* Full Footer - Inspired by Ansys (Dashboard only) */
        <footer className="bg-gradient-to-b from-neutral-900 to-neutral-800 text-white mt-16 border-t border-neutral-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Footer Header with Logo */}
          <div className="mb-12 pb-8 border-b border-neutral-700">
            <Link to="/" className="inline-block">
              <img 
                src="/LOGO.png" 
                alt="ANTEX Logo" 
                className="h-12 w-auto object-contain opacity-90 hover:opacity-100 transition-opacity duration-200"
                style={{ maxHeight: '48px' }}
              />
            </Link>
          </div>

          {/* Main Footer Content */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
            {/* Products Section */}
            <div>
              <h3 className="text-lg font-bold mb-4 text-white">Products</h3>
              <ul className="space-y-2">
                <li>
                  <Link to="/projects/new" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Create Project
                  </Link>
                </li>
                <li>
                  <Link to="/docs" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Documentation
                  </Link>
                </li>
                <li>
                  <Link to="/rf-analysis-tools" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    RF Analysis Tools
                  </Link>
                </li>
                <li>
                  <Link to="/performance-metrics" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Performance Metrics
                  </Link>
                </li>
              </ul>
            </div>

            {/* Learn Section */}
            <div>
              <h3 className="text-lg font-bold mb-4 text-white">Learn</h3>
              <ul className="space-y-2">
                <li>
                  <Link to="/docs" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    User Guide
                  </Link>
                </li>
                <li>
                  <Link to="/tutorials" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Tutorials
                  </Link>
                </li>
                <li>
                  <Link to="/best-practices" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Best Practices
                  </Link>
                </li>
                <li>
                  <Link to="/case-studies" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Case Studies
                  </Link>
                </li>
              </ul>
            </div>

            {/* Support Section */}
            <div>
              <h3 className="text-lg font-bold mb-4 text-white">Support</h3>
              <ul className="space-y-2">
                <li>
                  <Link to="/help" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link to="/api-docs" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    API Documentation
                  </Link>
                </li>
                <li>
                  <Link to="/contact" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Contact Support
                  </Link>
                </li>
                <li>
                  <Link to="/bug-reports" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Bug Reports
                  </Link>
                </li>
              </ul>
            </div>

            {/* About Section */}
            <div>
              <h3 className="text-lg font-bold mb-4 text-white">About</h3>
              <ul className="space-y-2">
                <li>
                  <Link to="/about" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    About ANTEX
                  </Link>
                </li>
                <li>
                  <Link to="/features" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Features
                  </Link>
                </li>
                <li>
                  <Link to="/technology" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    Technology
                  </Link>
                </li>
                <li>
                  <Link to="/license" className="text-neutral-300 hover:text-white transition-colors text-sm">
                    License
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          {/* Newsletter/Contact Section */}
          <div className="border-t border-neutral-700 pt-8 mb-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
              <div className="flex-1">
                <h3 className="text-xl font-bold mb-2 text-white">Let's Get Started</h3>
                <p className="text-neutral-300 text-sm max-w-2xl">
                  If you're facing engineering challenges, our team is here to assist. With a wealth of experience and a commitment to innovation, 
                  we invite you to reach out to us. Let's collaborate to turn your engineering obstacles into opportunities for growth and success.
                </p>
              </div>
              <Link
                to="/contact"
                className="inline-flex items-center px-6 py-3 bg-white text-primary-dark hover:bg-primary-dark hover:text-white transition-all duration-300 whitespace-nowrap rounded-lg font-semibold shadow-lg hover:shadow-xl"
              >
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Contact Us
              </Link>
            </div>
          </div>

          {/* Social Media & Bottom Bar */}
          <div className="border-t border-neutral-700 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              {/* Social Media Links */}
              <div className="flex items-center space-x-6">
                <span className="text-neutral-400 text-sm font-medium">Follow Us</span>
                <div className="flex space-x-4">
                  <a
                    href="https://www.linkedin.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral-400 hover:text-white transition-colors"
                    aria-label="LinkedIn"
                  >
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                  </a>
                  <a
                    href="https://github.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral-400 hover:text-white transition-colors"
                    aria-label="GitHub"
                  >
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd"/>
                    </svg>
                  </a>
                  <a
                    href="https://twitter.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral-400 hover:text-white transition-colors"
                    aria-label="Twitter"
                  >
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"/>
                    </svg>
                  </a>
                </div>
              </div>

              {/* Legal Links */}
              <div className="flex flex-wrap justify-center md:justify-end gap-6 text-sm">
                <Link to="/legal" className="text-neutral-400 hover:text-white transition-colors">
                  Legal Notice
                </Link>
                <Link to="/privacy" className="text-neutral-400 hover:text-white transition-colors">
                  Privacy Policy
                </Link>
                <Link to="/terms" className="text-neutral-400 hover:text-white transition-colors">
                  Terms & Conditions
                </Link>
                <Link to="/cookies" className="text-neutral-400 hover:text-white transition-colors">
                  Cookie Policy
                </Link>
              </div>
            </div>

            {/* Copyright */}
            <div className="mt-8 pt-8 border-t border-neutral-700 text-center">
              <p className="text-neutral-400 text-sm">
                © {new Date().getFullYear()} Copyright ANTEX. All rights reserved.
              </p>
            </div>
          </div>
        </div>
      </footer>
      ) : (
        /* Compact Footer (Other pages) */
        <footer className="bg-neutral-900 text-white border-t border-neutral-700 mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              {/* Logo and Copyright */}
              <div className="flex items-center gap-4">
                <Link to="/" className="inline-block">
                  <img 
                    src="/LOGO.png" 
                    alt="ANTEX Logo" 
                    className="h-8 w-auto object-contain opacity-90"
                    style={{ maxHeight: '32px' }}
                  />
                </Link>
                <p className="text-neutral-400 text-sm">
                  © {new Date().getFullYear()} ANTEX. All rights reserved.
                </p>
              </div>

              {/* Quick Links */}
              <div className="flex flex-wrap justify-center gap-4 text-sm">
                <Link to="/about" className="text-neutral-400 hover:text-white transition-colors">
                  About
                </Link>
                <Link to="/contact" className="text-neutral-400 hover:text-white transition-colors">
                  Contact
                </Link>
                <Link to="/privacy" className="text-neutral-400 hover:text-white transition-colors">
                  Privacy
                </Link>
                <Link to="/terms" className="text-neutral-400 hover:text-white transition-colors">
                  Terms
                </Link>
              </div>
            </div>
          </div>
        </footer>
      )}
    </div>
  )
}

import { Link } from 'react-router-dom'
import { useState } from 'react'
import toast from 'react-hot-toast'

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    toast.success('Thank you for contacting us! We will get back to you soon.')
    setFormData({ name: '', email: '', subject: '', message: '' })
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Contact Support</h1>
        <p className="text-neutral-600 mb-6">
          Have a question or need assistance? Get in touch with our support team.
        </p>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#607b7d' }}>
              Name
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input-field"
              placeholder="Your name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#607b7d' }}>
              Email
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="input-field"
              placeholder="your.email@example.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#607b7d' }}>
              Subject
            </label>
            <input
              type="text"
              required
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              className="input-field"
              placeholder="What can we help with?"
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#607b7d' }}>
              Message
            </label>
            <textarea
              required
              rows={6}
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="input-field resize-none"
              placeholder="Please provide details about your question or issue..."
            />
          </div>
          
          <div className="flex gap-4">
            <button type="submit" className="btn-primary">
              Send Message
            </button>
            <Link to="/" className="btn-secondary inline-flex items-center">
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}





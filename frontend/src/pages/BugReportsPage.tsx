import { Link } from 'react-router-dom'
import { useState } from 'react'
import toast from 'react-hot-toast'

export default function BugReportsPage() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    steps: '',
    expected: '',
    actual: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    toast.success('Bug report submitted successfully! Thank you for helping improve ANTEX.')
    setFormData({ title: '', description: '', steps: '', expected: '', actual: '' })
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Bug Reports</h1>
        <p className="text-neutral-600 mb-6">
          Found a bug? Help us improve ANTEX by reporting it. Please provide as much detail as possible.
        </p>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#607b7d' }}>
              Bug Title
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="input-field"
              placeholder="Brief description of the bug"
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#607b7d' }}>
              Description
            </label>
            <textarea
              required
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input-field resize-none"
              placeholder="Detailed description of the bug..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#607b7d' }}>
              Steps to Reproduce
            </label>
            <textarea
              required
              rows={4}
              value={formData.steps}
              onChange={(e) => setFormData({ ...formData, steps: e.target.value })}
              className="input-field resize-none"
              placeholder="1. Go to...&#10;2. Click on...&#10;3. See error..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#607b7d' }}>
              Expected Behavior
            </label>
            <textarea
              required
              rows={2}
              value={formData.expected}
              onChange={(e) => setFormData({ ...formData, expected: e.target.value })}
              className="input-field resize-none"
              placeholder="What should happen?"
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#607b7d' }}>
              Actual Behavior
            </label>
            <textarea
              required
              rows={2}
              value={formData.actual}
              onChange={(e) => setFormData({ ...formData, actual: e.target.value })}
              className="input-field resize-none"
              placeholder="What actually happens?"
            />
          </div>
          
          <div className="flex gap-4">
            <button type="submit" className="btn-primary">
              Submit Bug Report
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





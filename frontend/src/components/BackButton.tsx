import { useNavigate } from 'react-router-dom'

interface BackButtonProps {
  to?: string
  label?: string
  className?: string
}

export default function BackButton({ to, label = 'Back', className = '' }: BackButtonProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    if (to) {
      navigate(to)
    } else {
      navigate(-1) // Go back in history
    }
  }

  return (
    <button
      onClick={handleClick}
      className={`inline-flex items-center text-sm font-medium transition-colors duration-200 hover:text-primary-dark ${className}`}
      style={{ color: '#6b7a6b' }}
    >
      <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
      </svg>
      {label}
    </button>
  )
}





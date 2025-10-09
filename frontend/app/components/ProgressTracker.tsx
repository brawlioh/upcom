'use client'

import { CheckCircle, Circle, Loader2, Video, Monitor, Image, Settings } from 'lucide-react'
import { useAutomation } from '../hooks/useAutomation'

interface ProgressTrackerProps {
  currentStep: number
  totalSteps: number
  isRunning: boolean
}

const steps = [
  {
    id: 1,
    name: 'Intro Generation',
    description: 'Creating intro video with HeyGen',
    icon: Video,
    color: 'text-blue-400'
  },
  {
    id: 2,
    name: 'Gameplay Processing',
    description: 'Processing gameplay clip with Vizard',
    icon: Monitor,
    color: 'text-green-400'
  },
  {
    id: 3,
    name: 'Outro Generation',
    description: 'Creating outro video with HeyGen',
    icon: Image,
    color: 'text-purple-400'
  },
  {
    id: 4,
    name: 'Final Compilation',
    description: 'Compiling final reel with Creatomate',
    icon: Settings,
    color: 'text-orange-400'
  }
]

export default function ProgressTracker({ currentStep, totalSteps, isRunning }: ProgressTrackerProps) {
  const { currentJob } = useAutomation()
  
  // Use real job data if available, otherwise fall back to props
  const actualCurrentStep = currentJob?.current_step || currentStep
  const actualTotalSteps = currentJob?.total_steps || totalSteps
  const actualIsRunning = currentJob?.status === 'running' || currentJob?.status === 'queued' || isRunning
  const progress = actualCurrentStep > 0 ? (actualCurrentStep / actualTotalSteps) * 100 : 0

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-white">Pipeline Progress</h3>
        <div className="text-sm text-dark-400">
          {actualCurrentStep > 0 ? `${actualCurrentStep}/${actualTotalSteps}` : 'Ready'}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-1.5">
        <div className="flex justify-between text-sm text-dark-400 mb-1.5">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-dark-700 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-0.5">
        {steps.map((step) => {
          const isCompleted = actualCurrentStep > step.id
          const isCurrent = actualCurrentStep === step.id && actualIsRunning
          const isPending = actualCurrentStep < step.id
          
          return (
            <div
              key={step.id}
              className={`flex items-center space-x-3 p-2 rounded-lg transition-colors ${
                isCurrent ? 'bg-primary-600/10 border border-primary-600/20' : 
                isCompleted ? 'bg-green-600/10' : 'bg-dark-700/50'
              }`}
            >
              <div className="flex-shrink-0">
                {isCompleted ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
                ) : (
                  <Circle className="w-5 h-5 text-dark-500" />
                )}
              </div>
              
              <div className="flex-shrink-0">
                <step.icon className={`w-4 h-4 ${
                  isCompleted ? 'text-green-400' :
                  isCurrent ? 'text-primary-400' :
                  step.color
                }`} />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${
                  isCompleted ? 'text-green-400' :
                  isCurrent ? 'text-primary-400' :
                  'text-white'
                }`}>
                  {step.name}
                </p>
                <p className="text-xs text-dark-400 truncate">
                  {step.description}
                </p>
              </div>
              
              <div className="flex-shrink-0">
                {isCurrent && (
                  <div className="flex space-x-1">
                    <div className="w-1 h-1 bg-primary-400 rounded-full animate-bounce"></div>
                    <div className="w-1 h-1 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-1 h-1 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Status Message */}
      {actualIsRunning && (
        <div className="mt-4 p-3 bg-primary-600/10 border border-primary-600/20 rounded-lg">
          <p className="text-sm text-primary-400">
            {currentJob?.step_name || (actualCurrentStep > 0 && actualCurrentStep <= steps.length
              ? `Processing: ${steps[actualCurrentStep - 1].description}`
              : 'Initializing automation pipeline...')
            }
          </p>
        </div>
      )}

      {/* Job Status */}
      {currentJob && currentJob.status === 'completed' && (
        <div className="mt-4 p-3 bg-green-600/10 border border-green-600/20 rounded-lg">
          <p className="text-sm text-green-400">
            ✅ Automation completed successfully!
            {currentJob.result_path && (
              <span className="block text-xs mt-1 text-dark-400">
                Output: {currentJob.result_path}
              </span>
            )}
          </p>
        </div>
      )}

      {currentJob && currentJob.status === 'failed' && (
        <div className="mt-4 p-3 bg-red-600/10 border border-red-600/20 rounded-lg">
          <p className="text-sm text-red-400">
            ❌ Automation failed: {currentJob.error_message}
          </p>
        </div>
      )}
    </div>
  )
}

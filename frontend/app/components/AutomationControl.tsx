'use client'

import React, { useState } from 'react'
import { Play, Square, Settings, AlertCircle } from 'lucide-react'
import { useAutomation } from '../hooks/useAutomation'

interface AutomationControlProps {
  isRunning: boolean
  setIsRunning: (running: boolean) => void
  setCurrentStep: (step: number) => void
}

export default function AutomationControl({ isRunning, setIsRunning, setCurrentStep }: AutomationControlProps) {
  const [steamAppId, setSteamAppId] = useState('')
  const [customVideoUrl, setCustomVideoUrl] = useState('')
  const [mode, setMode] = useState<'steam'>('steam')
  const [error, setError] = useState<string | null>(null)
  
  const { startAutomation, stopJob, currentJob, isConnected } = useAutomation()

  const handleStart = async () => {
    try {
      setError(null)
      setIsRunning(true)
      
      // Prepare request for Steam App ID mode
      const request: any = { mode }
      
      if (!steamAppId.trim()) {
        throw new Error('Steam App ID is required')
      }
      request.steam_app_id = steamAppId.trim()
      
      if (customVideoUrl.trim()) {
        request.custom_video_url = customVideoUrl.trim()
      }
      
      // Start the automation
      const jobId = await startAutomation(request)
      console.log('Started automation job:', jobId)
      
    } catch (error) {
      console.error('Error starting automation:', error)
      setError(error instanceof Error ? error.message : 'Failed to start automation')
      setIsRunning(false)
    }
  }

  const handleStop = async () => {
    try {
      if (currentJob?.job_id) {
        await stopJob(currentJob.job_id)
      }
      setIsRunning(false)
      setCurrentStep(0)
    } catch (error) {
      console.error('Error stopping automation:', error)
    }
  }

  // Update local state based on current job
  React.useEffect(() => {
    if (currentJob) {
      setIsRunning(currentJob.status === 'running' || currentJob.status === 'queued')
      setCurrentStep(currentJob.current_step)
      
      if (currentJob.status === 'completed' || currentJob.status === 'failed') {
        setIsRunning(false)
        if (currentJob.status === 'failed') {
          setError(currentJob.error_message || 'Automation failed')
        }
      }
    }
  }, [currentJob])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xl font-bold text-white">Automation Control</h2>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 text-sm">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-dark-400">{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <button className="btn-secondary text-sm">
            <Settings className="w-4 h-4 mr-1" />
            Config
          </button>
        </div>
      </div>


      {/* Input Fields */}
      <div className="space-y-2 mb-2.5">
        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Steam App ID</label>
          <input
            type="text"
            value={steamAppId}
            onChange={(e) => setSteamAppId(e.target.value)}
            placeholder="Enter Steam App ID (e.g., 1962700)"
            className="input-field w-full"
            disabled={isRunning}
          />
          <p className="text-xs text-dark-400 mt-1">Find Steam App IDs at steamdb.info</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Custom Video URL (Optional)</label>
          <input
            type="url"
            value={customVideoUrl}
            onChange={(e) => setCustomVideoUrl(e.target.value)}
            placeholder="YouTube, Steam, or other video platform URL"
            className="input-field w-full"
            disabled={isRunning}
          />
          <p className="text-xs text-dark-400 mt-1">Leave empty to use Steam videos automatically</p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-600/10 border border-red-600/20 rounded-lg flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Control Buttons */}
      <div className="flex space-x-3">
        {!isRunning ? (
          <button
            onClick={handleStart}
            disabled={!steamAppId}
            className="btn-primary flex-1 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4 mr-2" />
            Start Automation
          </button>
        ) : (
          <button
            onClick={handleStop}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex-1 flex items-center justify-center"
          >
            <Square className="w-4 h-4 mr-2" />
            Stop Process
          </button>
        )}
        
        <button className="btn-secondary">
          <Settings className="w-4 h-4" />
        </button>
      </div>

    </div>
  )
}

'use client'

import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

interface AutomationJob {
  job_id: string
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  current_step: number
  total_steps: number
  step_name: string
  created_at: string
  completed_at?: string
  result_path?: string
  error_message?: string
  request?: AutomationRequest
}

interface AutomationRequest {
  mode: 'single' | 'steam' | 'trending'
  game_title?: string
  steam_app_id?: string
  custom_video_url?: string
  count?: number
}

const API_BASE_URL = 'http://localhost:8001/api'

export function useAutomation() {
  const [currentJob, setCurrentJob] = useState<AutomationJob | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [jobs, setJobs] = useState<AutomationJob[]>([])

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8001/ws')
    
    ws.onopen = () => {
      setIsConnected(true)
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'progress_update') {
          setCurrentJob(data.data)
          // Update jobs list
          setJobs(prev => prev.map(job => 
            job.job_id === data.job_id ? data.data : job
          ))
        } else if (data.type === 'job_completed') {
          console.log('Job completed:', data.result_path)
          // Update current job immediately
          if (data.data) {
            setCurrentJob(data.data)
          } else {
            // Fallback: fetch job status
            fetchJobStatus(data.job_id)
          }
        } else if (data.type === 'job_failed') {
          console.error('Job failed:', data.error)
          // Refresh job status
          fetchJobStatus(data.job_id)
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
    
    ws.onclose = () => {
      setIsConnected(false)
      console.log('WebSocket disconnected')
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsConnected(false)
    }
    
    return () => {
      ws.close()
    }
  }, [])

  const startAutomation = async (request: AutomationRequest) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/automation/start`, request)
      const { job_id } = response.data
      
      // Fetch initial job status
      const jobStatus = await fetchJobStatus(job_id)
      setCurrentJob(jobStatus)
      
      return job_id
    } catch (error) {
      console.error('Error starting automation:', error)
      throw error
    }
  }

  const fetchJobStatus = async (jobId: string): Promise<AutomationJob> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/automation/status/${jobId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching job status:', error)
      throw error
    }
  }

  const stopJob = async (jobId: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/automation/stop/${jobId}`)
      setCurrentJob(null)
    } catch (error) {
      console.error('Error stopping job:', error)
      throw error
    }
  }

  const fetchAllJobs = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/automation/jobs`)
      setJobs(response.data)
    } catch (error) {
      console.error('Error fetching jobs:', error)
    }
  }, [])

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`)
      return response.data
    } catch (error) {
      console.error('Error checking health:', error)
      return null
    }
  }

  // Fetch jobs on mount
  useEffect(() => {
    fetchAllJobs()
  }, [fetchAllJobs])

  return {
    currentJob,
    jobs,
    isConnected,
    startAutomation,
    stopJob,
    fetchJobStatus,
    fetchAllJobs,
    checkHealth
  }
}

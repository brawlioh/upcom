'use client'

import { useState, useEffect } from 'react'
import { Play, Download, ExternalLink, Clock, CheckCircle, AlertCircle, Zap } from 'lucide-react'
import { useAutomation } from '../hooks/useAutomation'

interface Reel {
  id: string
  title: string
  status: 'completed' | 'processing' | 'failed'
  createdAt: string
  duration: string
  thumbnail?: string
  downloadUrl?: string
}

export default function RecentReels() {
  const { jobs, fetchAllJobs } = useAutomation()
  const [reels, setReels] = useState<Reel[]>([])

  // Calculate real stats from jobs
  const completedJobs = jobs.filter(job => job.status === 'completed')
  const processingJobs = jobs.filter(job => job.status === 'running' || job.status === 'queued')
  const successRate = jobs.length > 0 ? Math.round((completedJobs.length / jobs.length) * 100) : 98

  // Convert API jobs to reel format
  useEffect(() => {
    const convertedReels = jobs
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 4) // Show only last 4
      .map(job => {
        // Extract game title from request or result path
        let title = 'Unknown Game'
        if (job.request?.game_title) {
          title = job.request.game_title
        } else if (job.result_path) {
          // Extract from file path like "Battlefield 6_final_reel.mp4"
          const filename = job.result_path.split('/').pop() || ''
          title = filename.replace('_final_reel.mp4', '')
        }

        // Calculate time ago
        const createdDate = new Date(job.created_at)
        const now = new Date()
        const diffMs = now.getTime() - createdDate.getTime()
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        const diffMins = Math.floor(diffMs / (1000 * 60))
        
        let timeAgo = ''
        if (diffHours >= 24) {
          timeAgo = `${Math.floor(diffHours / 24)} day${Math.floor(diffHours / 24) > 1 ? 's' : ''} ago`
        } else if (diffHours >= 1) {
          timeAgo = `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
        } else {
          timeAgo = `${diffMins} min${diffMins > 1 ? 's' : ''} ago`
        }

        return {
          id: job.job_id,
          title,
          status: job.status as 'completed' | 'processing' | 'failed',
          createdAt: timeAgo,
          duration: job.status === 'completed' ? '~60s' : '—',
          downloadUrl: job.result_path
        }
      })

    setReels(convertedReels)
  }, [jobs])

  // Refresh jobs when component mounts
  useEffect(() => {
    fetchAllJobs()
  }, [fetchAllJobs])

  const getStatusIcon = (status: Reel['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-400 animate-pulse" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-400" />
    }
  }

  const getStatusColor = (status: Reel['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-400'
      case 'processing':
        return 'text-yellow-400'
      case 'failed':
        return 'text-red-400'
    }
  }

  return (
    <div className="card">
      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
        <div className="text-center p-2 bg-dark-700/30 rounded-lg">
          <div className="w-6 h-6 bg-primary-600/20 rounded-lg flex items-center justify-center mx-auto mb-1">
            <Play className="w-3 h-3 text-primary-400" />
          </div>
          <div className="text-lg font-bold text-white">{completedJobs.length}</div>
          <div className="text-xs text-dark-400">Reels Created</div>
        </div>
        <div className="text-center p-2 bg-dark-700/30 rounded-lg">
          <div className="w-6 h-6 bg-green-600/20 rounded-lg flex items-center justify-center mx-auto mb-1">
            <CheckCircle className="w-3 h-3 text-green-400" />
          </div>
          <div className="text-lg font-bold text-white">{successRate}%</div>
          <div className="text-xs text-dark-400">Success Rate</div>
        </div>
        <div className="text-center p-2 bg-dark-700/30 rounded-lg">
          <div className="w-6 h-6 bg-yellow-600/20 rounded-lg flex items-center justify-center mx-auto mb-1">
            <Clock className="w-3 h-3 text-yellow-400" />
          </div>
          <div className="text-lg font-bold text-white">3.2m</div>
          <div className="text-xs text-dark-400">Avg Time</div>
        </div>
        <div className="text-center p-2 bg-dark-700/30 rounded-lg">
          <div className="w-6 h-6 bg-purple-600/20 rounded-lg flex items-center justify-center mx-auto mb-1">
            <Zap className="w-3 h-3 text-purple-400" />
          </div>
          <div className="text-lg font-bold text-white">{processingJobs.length}</div>
          <div className="text-xs text-dark-400">Processing</div>
        </div>
      </div>

      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-white">Recent Reels</h3>
        <button className="text-sm text-primary-400 hover:text-primary-300">
          View All
        </button>
      </div>

      <div className="space-y-2">
        {reels.map((reel) => (
          <div
            key={reel.id}
            className="flex items-center space-x-3 p-2 bg-dark-700/50 rounded-lg hover:bg-dark-700 transition-colors"
          >
            {/* Thumbnail placeholder */}
            <div className="w-10 h-6 bg-dark-600 rounded flex items-center justify-center flex-shrink-0">
              <Play className="w-3 h-3 text-dark-400" />
            </div>

            {/* Reel info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {reel.title}
              </p>
              <div className="flex items-center space-x-2 text-xs text-dark-400">
                {getStatusIcon(reel.status)}
                <span className={getStatusColor(reel.status)}>
                  {reel.status}
                </span>
                <span>•</span>
                <span>{reel.createdAt}</span>
                {reel.duration !== '—' && (
                  <>
                    <span>•</span>
                    <span>{reel.duration}</span>
                  </>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-1 flex-shrink-0">
              {reel.status === 'completed' && reel.downloadUrl && (
                <>
                  <button className="p-1 text-dark-400 hover:text-white transition-colors">
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-dark-400 hover:text-white transition-colors">
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

    </div>
  )
}

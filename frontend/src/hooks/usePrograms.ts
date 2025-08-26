import { useState, useCallback } from 'react'
import { Program, Asset, CreateProgramFormData } from '@/lib/types'

// Mock data to match the Figma design
const mockPrograms: Program[] = [
  {
    id: '1',
    name: 'Web AI Pentest - B2 team',
    startDate: '2023-11-02',
    website: 'https://trustline.sa',
    assets: [
      {
        id: 'a1',
        type: 'WEB',
        identifier: 'Trustline.sa',
        description: 'Complete Form',
        bountyEligibility: 'ELIGIBLE'
      }
    ],
    createdAt: '2023-11-02T00:00:00Z'
  },
  {
    id: '2',
    name: 'Web AI Pentest - B2 team',
    startDate: '2023-11-02',
    website: 'https://trustline.sa',
    assets: [
      {
        id: 'a2',
        type: 'WEB',
        identifier: 'Trustline.sa',
        description: 'Under Review',
        bountyEligibility: 'INELIGIBLE'
      }
    ],
    createdAt: '2023-11-02T00:00:00Z'
  },
  {
    id: '3',
    name: 'Web AI Pentest - B2 team',
    startDate: '2023-11-02',
    website: 'https://trustline.sa',
    assets: [
      {
        id: 'a3',
        type: 'WEB',
        identifier: 'Trustline.sa',
        description: '5 open Findings',
        bountyEligibility: 'ELIGIBLE'
      }
    ],
    createdAt: '2023-11-02T00:00:00Z'
  },
  {
    id: '4',
    name: 'Web AI Pentest - B2 team',
    startDate: '2023-11-02',
    website: 'https://trustline.sa',
    assets: [
      {
        id: 'a4',
        type: 'WEB',
        identifier: 'Trustline.sa',
        description: '74 Resolved Reports',
        bountyEligibility: 'INELIGIBLE'
      }
    ],
    createdAt: '2023-11-02T00:00:00Z'
  },
  {
    id: '5',
    name: 'Web AI Pentest - B2 team',
    startDate: '2023-11-02',
    website: 'https://trustline.sa',
    assets: [
      {
        id: 'a5',
        type: 'WEB',
        identifier: 'Trustline.sa',
        description: '71 Resolved Reports',
        bountyEligibility: 'ELIGIBLE'
      }
    ],
    createdAt: '2023-11-02T00:00:00Z'
  },
  {
    id: '6',
    name: 'Web AI Pentest - B2 team',
    startDate: '2023-11-02',
    website: 'https://trustline.sa',
    assets: [
      {
        id: 'a6',
        type: 'WEB',
        identifier: 'Trustline.sa',
        description: '71 Resolved Reports',
        bountyEligibility: 'INELIGIBLE'
      }
    ],
    createdAt: '2023-11-02T00:00:00Z'
  }
]

export function usePrograms() {
  const [programs, setPrograms] = useState<Program[]>(mockPrograms)

  const addProgram = useCallback((formData: CreateProgramFormData) => {
    const newProgram: Program = {
      id: Date.now().toString(),
      name: formData.name,
      startDate: formData.startDate.toISOString().split('T')[0],
      website: formData.website,
      twitterHandle: formData.twitterHandle,
      assets: formData.assets.map(asset => ({
        ...asset,
        id: Date.now().toString() + Math.random()
      })),
      createdAt: new Date().toISOString()
    }

    setPrograms(prev => [newProgram, ...prev])
  }, [])

  const deleteProgram = useCallback((id: string) => {
    setPrograms(prev => prev.filter(program => program.id !== id))
  }, [])

  const updateProgram = useCallback((id: string, updates: Partial<Program>) => {
    setPrograms(prev => prev.map(program => 
      program.id === id ? { ...program, ...updates } : program
    ))
  }, [])

  return {
    programs,
    addProgram,
    deleteProgram,
    updateProgram
  }
}
'use client'

import { useState } from 'react'
import SubscriptionDetails from '@/components/programs/SubscriptionDetails'
import ProgramsTable from '@/components/programs/ProgramsTable'
import CreateProgramModal from '@/components/programs/CreateProgramModal'
import { usePrograms } from '@/hooks/usePrograms'

const mockSubscription = {
  id: '1',
  name: 'Subscription 01',
  endDate: 'Aug 23, 2023',
  available: 8000,
  consumed: 400,
  total: 1200
}

export default function HomePage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const { programs, addProgram } = usePrograms()

  return (
    <div className="min-h-screen bg-figma-bg p-6">
      <div className="figma-container mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Programs</h1>
        </div>

        <SubscriptionDetails 
          subscription={mockSubscription} 
          onCreateProgram={() => setIsCreateModalOpen(true)}
        />
        <ProgramsTable programs={programs} />
        <CreateProgramModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={(data) => {
            addProgram(data)
            setIsCreateModalOpen(false)
          }}
        />
      </div>
    </div>
  )
}

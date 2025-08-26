import { formatCurrency } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Info, DollarSign } from 'lucide-react'

interface SubscriptionDetailsProps {
  subscription: {
    id: string
    name: string
    endDate: string
    available: number
    consumed: number
    total: number
  }
  onCreateProgram: () => void
}

export default function SubscriptionDetails({ subscription, onCreateProgram }: SubscriptionDetailsProps) {
  return (
    <div className="space-y-4">
      {/* Heading outside the card */}
      <h2 className="text-lg font-semibold text-gray-900">Subscription Details</h2>
      
      {/* White card container */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="flex items-center justify-between">
          {/* Left side content */}
          <div className="flex items-center space-x-12">
            {/* Status indicator and subscription info */}
            <div className="flex items-center space-x-4">
              {/* Green circle with dollar sign */}
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <DollarSign className="w-4 h-4 text-green-600" />
              </div>
              <div className="flex items-center space-x-6">
                <span className="font-bold text-gray-900">{subscription.name}</span>
                <span className="font-bold     text-sm">Ends {subscription.endDate}</span>
              </div>
            </div>

            {/* Pipeline separator */}
            <div className="w-px h-12 bg-gray-300"></div>

            {/* Available - Green label and value */}
            <div className="text-center min-w-[80px]">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <span className="text-s text-green-600 font-medium">Available</span>
                <Info className="w-3 h-3 text-gray-400" />
              </div>
              <div className="text-green-600 font-bold">{formatCurrency(subscription.available)}</div>
            </div>

            {/* Pipeline separator */}
            <div className="w-px h-12 bg-gray-300"></div>

            {/* Consumed - Regular styling */}
            <div className="text-center min-w-[80px]">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <span className="text-s text-gray-500">Consumed</span>
                <Info className="w-3 h-3 text-gray-400" />
              </div>
              <div className="text-gray-600 font-medium">{formatCurrency(subscription.consumed)}</div>
            </div>

            {/* Pipeline separator */}
            <div className="w-px h-12 bg-gray-300"></div>

            {/* Total Balance - Bold */}
            <div className="text-center min-w-[100px]">
              {/* <div className="text-xs text-gray-500 mb-1">Total Balance</div>
               */}
               <div className="text-s font-bold text-gray-900 mb-1">Total Balance</div>
              <div className="text-gray-900 font-bold">{formatCurrency(subscription.total)}</div>
            </div>
          </div>

          {/* Create Program Button - Light grey with purple text */}
          <Button 
            onClick={onCreateProgram} 
            className="bg-gray-100 hover:bg-gray-200 text-purple-600 hover:text-purple-700 px-6 py-2 rounded-lg font-bold border border-gray-200"
          >
            Create Program
          </Button>
        </div>
      </div>
    </div>
  )
}

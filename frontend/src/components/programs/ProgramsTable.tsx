import { Program } from '@/lib/types'
import { formatDate } from '@/lib/utils'
import { MoreHorizontal, Globe, Smartphone, ChevronDown, ArrowDown, Shield, ShieldX } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ProgramsTableProps {
  programs: Program[]
}

export default function ProgramsTable({ programs }: ProgramsTableProps) {
  const getBountyStatusBadge = (status: string) => {
    if (status === 'ELIGIBLE') {
      return (
        <span className="inline-flex items-center space-x-2 text-teal-600">
          <Shield className="w-4 h-4 text-teal-500" />
          <span className="text-sm">Eligible</span>
        </span>
      )
    } else {
      return (
        <span className="inline-flex items-center space-x-2 text-red-600">
          <ShieldX className="w-4 h-4 text-red-500" />
          <span className="text-sm">Ineligible</span>
        </span>
      )
    }
  }

  const getAssetIcon = (type: string) => {
    return type === 'WEB' ? <Globe className="w-4 h-4" /> : <Smartphone className="w-4 h-4" />
  }

  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="p-6">
        <h2 className="text-lg font-semibold mb-6">All programs</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-700">
                  <div className="flex items-center space-x-2">
                    <span>Program</span>
                    <ArrowDown className="w-4 h-4 text-gray-400" />
                  </div>
                </th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">
                  <div className="flex items-center space-x-2">
                    <span>Start Date</span>
                    <ArrowDown className="w-4 h-4 text-gray-400" />
                  </div>
                </th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Asset Identifier</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Description</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Bounty Eligibility</th>
                <th className="w-12 py-3 px-4"></th>
              </tr>
            </thead>
            <tbody>
              {programs.map((program) => (
                program.assets.map((asset, assetIndex) => (
                  <tr key={`${program.id}-${asset.id}`} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <a href="#" className="text-purple-500 hover:text-purple-600 font-medium">
                        {program.name}
                      </a>
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {formatDate(new Date(program.startDate))}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2">
                        {/* {getAssetIcon(asset.type)} */}
                        <a href="#" className="text-purple-500 hover:text-purple-600">
                          {asset.identifier}
                        </a>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {asset.description}
                    </td>
                    <td className="py-4 px-4">
                      {getBountyStatusBadge(asset.bountyEligibility)}
                    </td>
                    <td className="py-4 px-4">
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

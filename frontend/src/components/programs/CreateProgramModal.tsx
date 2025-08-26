'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { format } from 'date-fns'
import { Calendar as CalendarIcon, Trash2, Globe, Smartphone, Shield, ShieldX, X, ChevronDown } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Calendar } from '@/components/ui/calendar'
import { cn } from '@/lib/utils'
import { CreateProgramFormData, AssetType, BountyEligibility, AssetFormData } from '@/lib/types'

const createProgramSchema = z.object({
  name: z.string().min(1, 'Program name is required'),
  startDate: z.date(),
  website: z.string().optional(),
  twitterHandle: z.string().optional(),
})

interface CreateProgramModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: CreateProgramFormData) => void
}

export default function CreateProgramModal({ isOpen, onClose, onSubmit }: CreateProgramModalProps) {
  const [assets, setAssets] = useState<AssetFormData[]>([
    { type: 'ANDROID', identifier: 'Trustline.sa', description: 'Review Quotation Letter', bountyEligibility: 'ELIGIBLE' },
    { type: 'WEB', identifier: 'Google.sa', description: 'Form Incomplete', bountyEligibility: 'INELIGIBLE' }
  ])

  const [currentAsset, setCurrentAsset] = useState<AssetFormData>({
    type: 'WEB',
    identifier: '',
    description: '',
    bountyEligibility: 'ELIGIBLE'
  })

  const [showInlineCalendar, setShowInlineCalendar] = useState(false)
  const [tempSelectedDate, setTempSelectedDate] = useState<Date | undefined>()

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    reset
  } = useForm<z.infer<typeof createProgramSchema>>({
    resolver: zodResolver(createProgramSchema),
    defaultValues: {
      startDate: new Date(2021, 3, 6) 
    }
  })

  const watchedStartDate = watch('startDate')

  const openInlineCalendar = () => {
    setTempSelectedDate(watchedStartDate)
    setShowInlineCalendar(true)
  }

  const closeInlineCalendar = () => {
    setShowInlineCalendar(false)
    setTempSelectedDate(undefined)
  }

  const selectDate = () => {
    if (tempSelectedDate) {
      setValue('startDate', tempSelectedDate)
    }
    setShowInlineCalendar(false)
  }

  const addAsset = () => {
    if (!currentAsset.identifier.trim()) return

    const isDuplicate = assets.some(asset => asset.identifier.toLowerCase() === currentAsset.identifier.toLowerCase())
    if (isDuplicate) {
      alert('Asset identifier already exists')
      return
    }

    setAssets(prev => [...prev, { ...currentAsset }])
    setCurrentAsset({
      type: 'WEB',
      identifier: '',
      description: '',
      bountyEligibility: 'ELIGIBLE'
    })
  }

  const removeAsset = (index: number) => {
    setAssets(prev => prev.filter((_, i) => i !== index))
  }

  const handleFormSubmit = (data: z.infer<typeof createProgramSchema>) => {
    const formData: CreateProgramFormData = {
      ...data,
      assets: assets
    }
    onSubmit(formData)
    reset()
    setAssets([])
    setCurrentAsset({
      type: 'WEB',
      identifier: '',
      description: '',
      bountyEligibility: 'ELIGIBLE'
    })
  }

  const getAssetIcon = (type: AssetType | 'ANDROID') => {
    if (type === 'WEB') return <Globe className="w-4 h-4" />
    if (type === 'ANDROID') return (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
        <path d="M17.523,15.3414c-0.5511,0-0.9993-0.4486-0.9993-1.0006s0.4482-0.9993,0.9993-0.9993c0.5511,0,1,0.4473,1,0.9993S18.0741,15.3414,17.523,15.3414z M6.477,15.3414c-0.5511,0-0.9993-0.4486-0.9993-1.0006s0.4482-0.9993,0.9993-0.9993c0.5511,0,1,0.4473,1,0.9993S7.0281,15.3414,6.477,15.3414z M20.9564,11.1426c-0.7314-1.3085-1.6815-2.4092-2.7747-3.2453l1.3462-2.4658c0.1478-0.2704,0.0493-0.6118-0.2211-0.7596c-0.2704-0.1478-0.6118-0.0493-0.7596,0.2211l-1.4116,2.5862c-1.0485-0.5314-2.2213-0.8252-3.4651-0.8252c-1.2438,0-2.4166,0.2938-3.4651,0.8252L8.7538,4.9929c-0.1478-0.2704-0.4892-0.3689-0.7596-0.2211c-0.2704,0.1478-0.3689,0.4892-0.2211,0.7596l1.3462,2.4658c-1.0932,0.8361-2.0433,1.9368-2.7747,3.2453c-0.8201,1.4671-1.2468,3.0986-1.2468,4.7639v0.4932h15.8062v-0.4932C22.2032,14.2412,21.7765,12.6097,20.9564,11.1426z" />
      </svg>
    )
    return <Smartphone className="w-4 h-4" />
  }

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

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const currentDate = tempSelectedDate || watchedStartDate || new Date(2021, 3, 6)
  const currentMonth = currentDate.getMonth()
  const currentYear = currentDate.getFullYear()

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-figma-modal max-h-figma-modal overflow-y-auto program-card p-7">
        <div className="mb-6">
          <h2 className="text-xl font-semibold">Create Program</h2>
        </div>

        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-sm font-medium">Program Name *</Label>
              <Input
                id="name"
                {...register('name')}
                className="w-full"
                placeholder=""
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">Start Date *</Label>
              <div className="relative">
                <Button
                  type="button"
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !watchedStartDate && "text-muted-foreground"
                  )}
                  onClick={openInlineCalendar}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {watchedStartDate ? format(watchedStartDate, "dd/MM/yyyy") : "Select date"}
                </Button>
                
                {showInlineCalendar && (
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 z-50 mt-2 bg-white border rounded-lg shadow-xl p-6 min-w-[400px]">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">Finalize start date</h3>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={closeInlineCalendar}
                        className="h-8 w-8 rounded-full bg-gray-100 hover:bg-gray-200"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="flex space-x-4 mb-6">
                      <div className="flex-1 flex items-center justify-between p-3 border rounded border-gray-200 bg-white">
                        <span className="text-sm font-medium">{months[currentMonth]}</span>
                        <ChevronDown className="h-4 w-4 text-gray-500" />
                      </div>
                      <div className="flex-1 flex items-center justify-between p-3 border rounded border-gray-200 bg-white">
                        <span className="text-sm font-medium">{currentYear}</span>
                        <ChevronDown className="h-4 w-4 text-gray-500" />
                      </div>  
                    </div>

                    {/* Calendar Component */}
                    <div className="mb-6">
                      <Calendar
                        mode="single"
                        selected={tempSelectedDate}
                        onSelect={(date) => {
                          if (date) {
                            setTempSelectedDate(date)
                          }
                        }}
                        month={new Date(currentYear, currentMonth)}
                        className="w-full calendar-popup"
                      />
                    </div>

                    {/* Full-width buttons */}
                    <div className="grid grid-cols-2 gap-4">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={closeInlineCalendar}
                        className="w-full text-purple-500 border-purple-200 bg-purple-50"
                      >
                        Cancel
                      </Button>
                      <Button
                        type="button"
                        onClick={selectDate}
                        className="w-full bg-purple-500 hover:bg-purple-600 text-white"
                      >
                        Select
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="website" className="text-sm font-medium">Website</Label>
              <Input
                id="website"
                {...register('website')}
                placeholder="Enter Your Website"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="twitterHandle" className="text-sm font-medium">Twitter / X</Label>
              <Input
                id="twitterHandle"
                {...register('twitterHandle')}
                placeholder="Enter @Username"
              />
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium">Asset You Want to Test</Label>
              <Select
                value={currentAsset.type}
                onValueChange={(value: AssetType) => 
                  setCurrentAsset(prev => ({ ...prev, type: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Please Select" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="WEB">Web</SelectItem>
                  <SelectItem value="MOBILE">Mobile App</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">Asset Identifier</Label>
              <Input
                value={currentAsset.identifier}
                onChange={(e) => setCurrentAsset(prev => ({ ...prev, identifier: e.target.value }))}
                placeholder="Write your asset Identifier"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">Description</Label>
              <Input
                value={currentAsset.description}
                onChange={(e) => setCurrentAsset(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Description"
              />
            </div>

            <div className="flex items-end justify-between gap-4">
              <div className="space-y-2 flex-1">
                <Label className="text-sm font-medium">Bounty Eligibility</Label>
                <Select
                  value={currentAsset.bountyEligibility}
                  onValueChange={(value: BountyEligibility) => 
                    setCurrentAsset(prev => ({ ...prev, bountyEligibility: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Please Select" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ELIGIBLE">Eligible</SelectItem>
                    <SelectItem value="INELIGIBLE">Ineligible</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button
                type="button"
                onClick={addAsset}
                className="bg-purple-500 hover:bg-purple-600 text-white"
              >
                Add
              </Button>
            </div>
          </div>

          {assets.length > 0 && (
            <div className="space-y-4">
              <div className="grid grid-cols-12 gap-2 text-sm font-medium text-gray-700 pb-2 border-b">
                <div className="col-span-1">Type</div>
                <div className="col-span-3">Asset Identifier</div>
                <div className="col-span-4">Description</div>
                <div className="col-span-3">Bounty</div>
                <div className="col-span-1"></div>
              </div>

              {assets.map((asset, index) => (
                <div key={index} className="grid grid-cols-12 gap-2 items-center py-2 border-b border-gray-100">
                  <div className="col-span-1 flex items-center">
                    {getAssetIcon(asset.type as AssetType | 'ANDROID')}
                  </div>
                  <div className="col-span-3 text-purple-500 font-medium">
                    {asset.identifier}
                  </div>
                  <div className="col-span-4 text-gray-600">
                    {asset.description}
                  </div>
                  <div className="col-span-3">
                    {getBountyStatusBadge(asset.bountyEligibility)}
                  </div>
                  <div className="col-span-1">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeAsset(index)}
                      className="h-8 w-8 text-gray-400 hover:text-red-500"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="w-full text-purple-500 border-purple-200"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="w-full bg-purple-500 hover:bg-purple-600 text-white"
            >
              Submit
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

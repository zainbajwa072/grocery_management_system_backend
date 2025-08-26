'use client'

import { useState } from 'react'
import { format } from 'date-fns'
import { X, ChevronDown } from 'lucide-react'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

interface DatePickerModalProps {
  isOpen: boolean
  onClose: () => void
  selectedDate: Date | undefined
  onDateSelect: (date: Date) => void
}

export default function DatePickerModal({ 
  isOpen, 
  onClose, 
  selectedDate, 
  onDateSelect 
}: DatePickerModalProps) {
  const [tempDate, setTempDate] = useState<Date>(selectedDate || new Date(2021, 3, 6))
  const [currentMonth, setCurrentMonth] = useState(tempDate.getMonth())
  const [currentYear, setCurrentYear] = useState(tempDate.getFullYear())

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const years = Array.from({ length: 10 }, (_, i) => currentYear - 5 + i)

  const handleMonthChange = (monthIndex: string) => {
    const newMonth = parseInt(monthIndex)
    setCurrentMonth(newMonth)
    const newDate = new Date(currentYear, newMonth, tempDate.getDate())
    setTempDate(newDate)
  }

  const handleYearChange = (year: string) => {
    const newYear = parseInt(year)
    setCurrentYear(newYear)
    const newDate = new Date(newYear, currentMonth, tempDate.getDate())
    setTempDate(newDate)
  }

  const handleDateSelect = (date: Date | undefined) => {
    if (date) {
      setTempDate(date)
    }
  }

  const handleConfirm = () => {
    onDateSelect(tempDate)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md w-full p-6 date-picker-modal">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">Finalize start date</h3>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 rounded-full bg-gray-100 hover:bg-gray-200"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex space-x-4 mb-6">
          <Select value={currentMonth.toString()} onValueChange={handleMonthChange}>
            <SelectTrigger className="flex-1">
              <SelectValue>
                <div className="flex items-center justify-between w-full">
                  <span>{months[currentMonth]}</span>
                  <ChevronDown className="h-4 w-4" />
                </div>
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {months.map((month, index) => (
                <SelectItem key={index} value={index.toString()}>
                  {month}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={currentYear.toString()} onValueChange={handleYearChange}>
            <SelectTrigger className="flex-1">
              <SelectValue>
                <div className="flex items-center justify-between w-full">
                  <span>{currentYear}</span>
                  <ChevronDown className="h-4 w-4" />
                </div>
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {years.map((year) => (
                <SelectItem key={year} value={year.toString()}>
                  {year}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="mb-6">
          <Calendar
            mode="single"
            selected={tempDate}
            onSelect={handleDateSelect}
            month={new Date(currentYear, currentMonth)}
            className="w-full"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Button
            variant="outline"
            onClick={onClose}
            className="w-full text-purple-500 border-purple-200"
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            className="w-full bg-purple-500 hover:bg-purple-600 text-white"
          >
            Select
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

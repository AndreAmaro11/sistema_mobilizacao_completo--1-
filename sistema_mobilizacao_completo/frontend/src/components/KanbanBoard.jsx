import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Plus, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  User,
  Calendar,
  DollarSign,
  Building
} from 'lucide-react'
import { cardsAPI, etapasAPI } from '../lib/api'
import KanbanCard from './KanbanCard'
import CreateCardDialog from './CreateCardDialog'

export default function KanbanBoard() {
  const [etapas, setEtapas] = useState([])
  const [cards, setCards] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateDialog, setShowCreateDialog] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [etapasResponse, cardsResponse] = await Promise.all([
        etapasAPI.list(),
        cardsAPI.list()
      ])

      if (etapasResponse.data.success) {
        setEtapas(etapasResponse.data.data)
      }

      if (cardsResponse.data.success) {
        setCards(cardsResponse.data.data.cards)
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
      setError('Erro ao carregar dados do sistema')
    } finally {
      setLoading(false)
    }
  }

  const getCardsByEtapa = (etapaId) => {
    return cards.filter(card => card.etapa_atual?.id === etapaId)
  }

  const getStatusColor = (statusPrazo) => {
    switch (statusPrazo) {
      case 'VENCIDO':
        return 'bg-red-100 border-red-200'
      case 'VENCENDO':
        return 'bg-yellow-100 border-yellow-200'
      default:
        return 'bg-white border-gray-200'
    }
  }

  const getStatusIcon = (statusPrazo) => {
    switch (statusPrazo) {
      case 'VENCIDO':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'VENCENDO':
        return <Clock className="h-4 w-4 text-yellow-500" />
      default:
        return <CheckCircle className="h-4 w-4 text-green-500" />
    }
  }

  const getEtapaColor = (ordem) => {
    const colors = [
      'bg-blue-500',
      'bg-orange-500', 
      'bg-green-500',
      'bg-purple-500',
      'bg-teal-500',
      'bg-pink-500',
      'bg-gray-500'
    ]
    return colors[ordem % colors.length] || 'bg-gray-500'
  }

  const handleCardCreated = (newCard) => {
    setCards(prev => [...prev, newCard])
    setShowCreateDialog(false)
  }

  const handleCardUpdated = (updatedCard) => {
    setCards(prev => prev.map(card => 
      card.id === updatedCard.id ? updatedCard : card
    ))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header do Kanban */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Board Kanban</h2>
          <p className="text-gray-600">
            {cards.length} colaboradores em processo de mobilização
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)} className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Novo Colaborador</span>
        </Button>
      </div>

      {/* Board Kanban */}
      <div className="flex space-x-6 overflow-x-auto pb-4">
        {etapas.map((etapa) => {
          const etapaCards = getCardsByEtapa(etapa.id)
          
          return (
            <div key={etapa.id} className="flex-shrink-0 w-80">
              {/* Header da Coluna */}
              <div className="mb-4">
                <div className={`h-1 w-full rounded-t-lg ${getEtapaColor(etapa.ordem - 1)}`} />
                <Card className="rounded-t-none">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg font-semibold">
                        {etapa.nome}
                      </CardTitle>
                      <Badge variant="secondary" className="ml-2">
                        {etapaCards.length}
                      </Badge>
                    </div>
                    {etapa.descricao && (
                      <p className="text-sm text-gray-600">{etapa.descricao}</p>
                    )}
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>{etapa.prazo_dias} dias</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <User className="h-3 w-3" />
                        <span>{etapa.dono_email}</span>
                      </span>
                    </div>
                  </CardHeader>
                </Card>
              </div>

              {/* Cards da Coluna */}
              <ScrollArea className="h-[calc(100vh-300px)]">
                <div className="space-y-3">
                  {etapaCards.map((card) => (
                    <KanbanCard
                      key={card.id}
                      card={card}
                      onUpdate={handleCardUpdated}
                    />
                  ))}
                  
                  {etapaCards.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <div className="text-4xl mb-2">📋</div>
                      <p>Nenhum card nesta etapa</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </div>
          )
        })}
      </div>

      {/* Dialog para criar novo card */}
      <CreateCardDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onCardCreated={handleCardCreated}
        etapas={etapas}
      />
    </div>
  )
}


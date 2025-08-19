import { useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog'
import { 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  User,
  Calendar,
  DollarSign,
  Building,
  FileText,
  MoreHorizontal
} from 'lucide-react'
import CardDetailsDialog from './CardDetailsDialog'

export default function KanbanCard({ card, onUpdate }) {
  const [showDetails, setShowDetails] = useState(false)

  const getStatusColor = (statusPrazo) => {
    switch (statusPrazo) {
      case 'VENCIDO':
        return 'border-red-200 bg-red-50'
      case 'VENCENDO':
        return 'border-yellow-200 bg-yellow-50'
      default:
        return 'border-gray-200 bg-white'
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

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'NAO_INICIADO':
        return 'secondary'
      case 'EM_ANDAMENTO':
        return 'default'
      case 'FINALIZADO':
        return 'success'
      default:
        return 'secondary'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'NAO_INICIADO':
        return 'Não Iniciado'
      case 'EM_ANDAMENTO':
        return 'Em Andamento'
      case 'FINALIZADO':
        return 'Finalizado'
      default:
        return status
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  const formatCurrency = (value) => {
    if (!value) return ''
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <>
      <Card 
        className={`cursor-pointer transition-all hover:shadow-md ${getStatusColor(card.status_prazo)}`}
        onClick={() => setShowDetails(true)}
      >
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-semibold text-sm leading-tight">
                {card.nome_colaborador}
              </h3>
              <p className="text-xs text-gray-600 mt-1">{card.cargo}</p>
            </div>
            <div className="flex items-center space-x-1 ml-2">
              {getStatusIcon(card.status_prazo)}
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                <MoreHorizontal className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-0 space-y-3">
          {/* Status */}
          <div className="flex items-center justify-between">
            <Badge variant={getStatusBadgeVariant(card.status_etapa)} className="text-xs">
              {getStatusText(card.status_etapa)}
            </Badge>
            {card.prazo_etapa && (
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <Calendar className="h-3 w-3" />
                <span>{formatDate(card.prazo_etapa)}</span>
              </div>
            )}
          </div>

          {/* Informações do Colaborador */}
          <div className="space-y-1 text-xs text-gray-600">
            {card.salario && (
              <div className="flex items-center space-x-1">
                <DollarSign className="h-3 w-3" />
                <span>{formatCurrency(card.salario)}</span>
              </div>
            )}
            {card.centro_custo && (
              <div className="flex items-center space-x-1">
                <Building className="h-3 w-3" />
                <span>{card.centro_custo}</span>
              </div>
            )}
            {card.data_admissao && (
              <div className="flex items-center space-x-1">
                <Calendar className="h-3 w-3" />
                <span>Admissão: {formatDate(card.data_admissao)}</span>
              </div>
            )}
          </div>

          {/* Progresso do Checklist */}
          {card.checklist_progresso && (
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600">Progresso</span>
                <span className="font-medium">
                  {card.checklist_progresso.concluidos}/{card.checklist_progresso.total}
                </span>
              </div>
              <Progress 
                value={card.checklist_progresso.percentual} 
                className="h-2"
              />
              <div className="text-xs text-gray-500">
                {card.checklist_progresso.percentual}% concluído
              </div>
            </div>
          )}

          {/* Responsável */}
          {card.responsavel_atual && (
            <div className="flex items-center space-x-2 pt-2 border-t border-gray-100">
              <Avatar className="h-6 w-6">
                <AvatarFallback className="text-xs">
                  {getInitials(card.responsavel_atual.split('@')[0])}
                </AvatarFallback>
              </Avatar>
              <span className="text-xs text-gray-600 truncate">
                {card.responsavel_atual}
              </span>
            </div>
          )}

          {/* Observações */}
          {card.observacoes && (
            <div className="flex items-start space-x-1 text-xs text-gray-500">
              <FileText className="h-3 w-3 mt-0.5 flex-shrink-0" />
              <span className="line-clamp-2">{card.observacoes}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de Detalhes */}
      <CardDetailsDialog
        card={card}
        open={showDetails}
        onOpenChange={setShowDetails}
        onUpdate={onUpdate}
      />
    </>
  )
}


import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  User, 
  Calendar, 
  DollarSign, 
  Building, 
  FileText,
  Clock,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  Loader2
} from 'lucide-react'
import { cardsAPI, etapasAPI } from '../lib/api'

export default function CardDetailsDialog({ card, open, onOpenChange, onUpdate }) {
  const [activeTab, setActiveTab] = useState('details')
  const [etapas, setEtapas] = useState([])
  const [checklist, setChecklist] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState({})

  useEffect(() => {
    if (open && card) {
      loadCardDetails()
      setFormData({
        nome_colaborador: card.nome_colaborador || '',
        cargo: card.cargo || '',
        salario: card.salario || '',
        centro_custo: card.centro_custo || '',
        data_admissao: card.data_admissao || '',
        observacoes: card.observacoes || ''
      })
    }
  }, [open, card])

  const loadCardDetails = async () => {
    try {
      setLoading(true)
      const [etapasResponse, cardResponse] = await Promise.all([
        etapasAPI.list(),
        cardsAPI.get(card.id)
      ])

      if (etapasResponse.data.success) {
        setEtapas(etapasResponse.data.data)
      }

      if (cardResponse.data.success) {
        setChecklist(cardResponse.data.data.checklist || [])
      }
    } catch (error) {
      console.error('Erro ao carregar detalhes:', error)
      setError('Erro ao carregar detalhes do card')
    } finally {
      setLoading(false)
    }
  }

  const handleChecklistToggle = async (itemId, checked) => {
    try {
      const response = await cardsAPI.updateChecklist(card.id, itemId, {
        concluido: checked
      })

      if (response.data.success) {
        // Atualizar checklist local
        setChecklist(prev => prev.map(item => 
          item.id === itemId 
            ? { ...item, concluido: checked, data_conclusao: checked ? new Date().toISOString() : null }
            : item
        ))

        // Atualizar card no componente pai
        const updatedCard = {
          ...card,
          checklist_progresso: response.data.data.checklist_progresso
        }
        onUpdate(updatedCard)
      }
    } catch (error) {
      console.error('Erro ao atualizar checklist:', error)
      setError('Erro ao atualizar item do checklist')
    }
  }

  const handleMoveCard = async (novaEtapaId) => {
    try {
      setLoading(true)
      const response = await cardsAPI.move(card.id, {
        etapa_destino_id: novaEtapaId,
        motivo: 'Movimentação via interface'
      })

      if (response.data.success) {
        onUpdate(response.data.data)
        onOpenChange(false)
      } else {
        setError(response.data.error?.message || 'Erro ao mover card')
      }
    } catch (error) {
      console.error('Erro ao mover card:', error)
      setError(error.response?.data?.error?.message || 'Erro ao mover card')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveChanges = async () => {
    try {
      setLoading(true)
      const response = await cardsAPI.update(card.id, {
        ...formData,
        salario: formData.salario ? parseFloat(formData.salario) : null
      })

      if (response.data.success) {
        onUpdate(response.data.data)
        setEditMode(false)
      } else {
        setError(response.data.error?.message || 'Erro ao salvar alterações')
      }
    } catch (error) {
      console.error('Erro ao salvar:', error)
      setError(error.response?.data?.error?.message || 'Erro ao salvar alterações')
    } finally {
      setLoading(false)
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

  const getStatusColor = (status) => {
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

  if (!card) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>{card.nome_colaborador}</span>
            <div className="flex items-center space-x-2">
              <Badge variant={getStatusColor(card.status_etapa)}>
                {getStatusText(card.status_etapa)}
              </Badge>
              {!editMode ? (
                <Button variant="outline" size="sm" onClick={() => setEditMode(true)}>
                  Editar
                </Button>
              ) : (
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={() => setEditMode(false)}>
                    Cancelar
                  </Button>
                  <Button size="sm" onClick={handleSaveChanges} disabled={loading}>
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Salvar'}
                  </Button>
                </div>
              )}
            </div>
          </DialogTitle>
        </DialogHeader>

        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="details">Detalhes</TabsTrigger>
            <TabsTrigger value="checklist">Checklist</TabsTrigger>
            <TabsTrigger value="actions">Ações</TabsTrigger>
          </TabsList>

          <TabsContent value="details" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Nome do Colaborador</Label>
                {editMode ? (
                  <Input
                    value={formData.nome_colaborador}
                    onChange={(e) => setFormData(prev => ({...prev, nome_colaborador: e.target.value}))}
                  />
                ) : (
                  <div className="p-2 bg-gray-50 rounded">{card.nome_colaborador}</div>
                )}
              </div>

              <div className="space-y-2">
                <Label>CPF</Label>
                <div className="p-2 bg-gray-50 rounded">{card.cpf || 'Não informado'}</div>
              </div>

              <div className="space-y-2">
                <Label>Cargo</Label>
                {editMode ? (
                  <Input
                    value={formData.cargo}
                    onChange={(e) => setFormData(prev => ({...prev, cargo: e.target.value}))}
                  />
                ) : (
                  <div className="p-2 bg-gray-50 rounded">{card.cargo || 'Não informado'}</div>
                )}
              </div>

              <div className="space-y-2">
                <Label>Salário</Label>
                {editMode ? (
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.salario}
                    onChange={(e) => setFormData(prev => ({...prev, salario: e.target.value}))}
                  />
                ) : (
                  <div className="p-2 bg-gray-50 rounded">
                    {card.salario ? formatCurrency(card.salario) : 'Não informado'}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label>Centro de Custo</Label>
                {editMode ? (
                  <Input
                    value={formData.centro_custo}
                    onChange={(e) => setFormData(prev => ({...prev, centro_custo: e.target.value}))}
                  />
                ) : (
                  <div className="p-2 bg-gray-50 rounded">{card.centro_custo || 'Não informado'}</div>
                )}
              </div>

              <div className="space-y-2">
                <Label>Data de Admissão</Label>
                {editMode ? (
                  <Input
                    type="date"
                    value={formData.data_admissao}
                    onChange={(e) => setFormData(prev => ({...prev, data_admissao: e.target.value}))}
                  />
                ) : (
                  <div className="p-2 bg-gray-50 rounded">
                    {card.data_admissao ? formatDate(card.data_admissao) : 'Não informado'}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Etapa Atual</Label>
              <div className="p-2 bg-blue-50 rounded border border-blue-200">
                <div className="font-medium">{card.etapa_atual?.nome}</div>
                <div className="text-sm text-gray-600">{card.etapa_atual?.descricao}</div>
                {card.prazo_etapa && (
                  <div className="text-sm text-gray-500 mt-1">
                    Prazo: {formatDate(card.prazo_etapa)}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Observações</Label>
              {editMode ? (
                <Textarea
                  value={formData.observacoes}
                  onChange={(e) => setFormData(prev => ({...prev, observacoes: e.target.value}))}
                  rows={3}
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded min-h-[80px]">
                  {card.observacoes || 'Nenhuma observação'}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="checklist" className="space-y-4">
            {card.checklist_progresso && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Progresso do Checklist</Label>
                  <span className="text-sm font-medium">
                    {card.checklist_progresso.concluidos}/{card.checklist_progresso.total}
                  </span>
                </div>
                <Progress value={card.checklist_progresso.percentual} className="h-2" />
                <div className="text-sm text-gray-500">
                  {card.checklist_progresso.percentual}% concluído
                </div>
              </div>
            )}

            <div className="space-y-3">
              {checklist.map((item) => (
                <div key={item.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                  <Checkbox
                    checked={item.concluido}
                    onCheckedChange={(checked) => handleChecklistToggle(item.id, checked)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className={`font-medium ${item.concluido ? 'line-through text-gray-500' : ''}`}>
                      {item.tarefa}
                      {item.obrigatorio && <span className="text-red-500 ml-1">*</span>}
                    </div>
                    {item.descricao && (
                      <div className="text-sm text-gray-600 mt-1">{item.descricao}</div>
                    )}
                    {item.concluido && item.data_conclusao && (
                      <div className="text-xs text-gray-500 mt-1">
                        Concluído em {formatDate(item.data_conclusao)}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {checklist.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>Nenhum item no checklist para esta etapa</p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="actions" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label className="text-base font-medium">Mover para Outra Etapa</Label>
                <p className="text-sm text-gray-600 mb-3">
                  Selecione a etapa de destino para mover este card
                </p>
                
                <div className="grid grid-cols-1 gap-2">
                  {etapas.map((etapa) => (
                    <Button
                      key={etapa.id}
                      variant={etapa.id === card.etapa_atual?.id ? "secondary" : "outline"}
                      className="justify-start h-auto p-4"
                      disabled={etapa.id === card.etapa_atual?.id || loading}
                      onClick={() => handleMoveCard(etapa.id)}
                    >
                      <div className="flex items-center space-x-3 w-full">
                        <div className="flex-1 text-left">
                          <div className="font-medium">{etapa.nome}</div>
                          <div className="text-sm text-gray-600">{etapa.descricao}</div>
                        </div>
                        {etapa.id !== card.etapa_atual?.id && (
                          <ArrowRight className="h-4 w-4" />
                        )}
                        {etapa.id === card.etapa_atual?.id && (
                          <Badge variant="secondary">Atual</Badge>
                        )}
                      </div>
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}


import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, AlertTriangle } from 'lucide-react'
import { cardsAPI } from '../lib/api'

export default function CreateCardDialog({ open, onOpenChange, onCardCreated, etapas }) {
  const [formData, setFormData] = useState({
    nome_colaborador: '',
    cpf: '',
    cargo: '',
    salario: '',
    centro_custo: '',
    data_admissao: '',
    observacoes: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Preparar dados para envio
      const dataToSend = {
        ...formData,
        salario: formData.salario ? parseFloat(formData.salario) : null
      }

      const response = await cardsAPI.create(dataToSend)
      
      if (response.data.success) {
        onCardCreated(response.data.data)
        resetForm()
      } else {
        setError(response.data.error?.message || 'Erro ao criar card')
      }
    } catch (error) {
      console.error('Erro ao criar card:', error)
      setError(error.response?.data?.error?.message || 'Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({
      nome_colaborador: '',
      cpf: '',
      cargo: '',
      salario: '',
      centro_custo: '',
      data_admissao: '',
      observacoes: ''
    })
    setError('')
  }

  const handleOpenChange = (newOpen) => {
    if (!newOpen) {
      resetForm()
    }
    onOpenChange(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Novo Colaborador</DialogTitle>
          <DialogDescription>
            Adicione um novo colaborador ao processo de mobilização. 
            Ele será automaticamente colocado na primeira etapa do processo.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="nome_colaborador">Nome do Colaborador *</Label>
              <Input
                id="nome_colaborador"
                value={formData.nome_colaborador}
                onChange={(e) => handleInputChange('nome_colaborador', e.target.value)}
                placeholder="Nome completo"
                required
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="cpf">CPF</Label>
              <Input
                id="cpf"
                value={formData.cpf}
                onChange={(e) => handleInputChange('cpf', e.target.value)}
                placeholder="000.000.000-00"
                disabled={loading}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="cargo">Cargo</Label>
              <Input
                id="cargo"
                value={formData.cargo}
                onChange={(e) => handleInputChange('cargo', e.target.value)}
                placeholder="Cargo/função"
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="salario">Salário</Label>
              <Input
                id="salario"
                type="number"
                step="0.01"
                value={formData.salario}
                onChange={(e) => handleInputChange('salario', e.target.value)}
                placeholder="0.00"
                disabled={loading}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="centro_custo">Centro de Custo</Label>
              <Input
                id="centro_custo"
                value={formData.centro_custo}
                onChange={(e) => handleInputChange('centro_custo', e.target.value)}
                placeholder="Departamento/setor"
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="data_admissao">Data de Admissão</Label>
              <Input
                id="data_admissao"
                type="date"
                value={formData.data_admissao}
                onChange={(e) => handleInputChange('data_admissao', e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="observacoes">Observações</Label>
            <Textarea
              id="observacoes"
              value={formData.observacoes}
              onChange={(e) => handleInputChange('observacoes', e.target.value)}
              placeholder="Informações adicionais sobre o colaborador..."
              rows={3}
              disabled={loading}
            />
          </div>

          <DialogFooter>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => handleOpenChange(false)}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Criando...
                </>
              ) : (
                'Criar Colaborador'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}


import { useState, useEffect } from 'react'
import { Bell, Check, AlertTriangle, Clock, CheckCircle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { notificacoesAPI } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export default function NotificacoesDropdown() {
  const { isAuthenticated } = useAuth()
  const [notificacoes, setNotificacoes] = useState([])
  const [contagem, setContagem] = useState(0)
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)

  // Carregar contagem de notificações não lidas
  useEffect(() => {
    if (isAuthenticated) {
      carregarContagem()
      
      // Atualizar a cada 5 minutos
      const interval = setInterval(carregarContagem, 5 * 60 * 1000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  // Carregar notificações quando abrir o dropdown
  useEffect(() => {
    if (open && isAuthenticated) {
      carregarNotificacoes()
    }
  }, [open, isAuthenticated])

  const carregarContagem = async () => {
    try {
      const response = await notificacoesAPI.contagem()
      if (response.data.success) {
        setContagem(response.data.data.nao_lidas)
      }
    } catch (error) {
      console.error('Erro ao carregar contagem de notificações:', error)
    }
  }

  const carregarNotificacoes = async () => {
    try {
      setLoading(true)
      const response = await notificacoesAPI.listar()
      if (response.data.success) {
        setNotificacoes(response.data.data)
      }
    } catch (error) {
      console.error('Erro ao carregar notificações:', error)
    } finally {
      setLoading(false)
    }
  }

  const marcarComoLida = async (id) => {
    try {
      await notificacoesAPI.marcarComoLida(id)
      // Atualizar lista local
      setNotificacoes(prev => prev.filter(n => n.id !== id))
      // Atualizar contagem
      setContagem(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Erro ao marcar notificação como lida:', error)
    }
  }

  const marcarTodasComoLidas = async () => {
    try {
      await notificacoesAPI.marcarTodasComoLidas()
      // Limpar lista local
      setNotificacoes([])
      // Zerar contagem
      setContagem(0)
    } catch (error) {
      console.error('Erro ao marcar todas notificações como lidas:', error)
    }
  }

  const formatarTempo = (data) => {
    try {
      return formatDistanceToNow(new Date(data), { addSuffix: true, locale: ptBR })
    } catch (error) {
      return 'data desconhecida'
    }
  }

  const getIconeNotificacao = (tipo) => {
    switch (tipo) {
      case 'PRAZO_VENCIDO':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'PRAZO_VENCENDO':
        return <Clock className="h-4 w-4 text-amber-500" />
      case 'CARD_INATIVO':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'CHECKLIST_PENDENTE':
        return <CheckCircle className="h-4 w-4 text-purple-500" />
      case 'CARD_MOVIDO':
        return <Check className="h-4 w-4 text-green-500" />
      default:
        return <Bell className="h-4 w-4" />
    }
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {contagem > 0 && (
            <Badge variant="destructive" className="absolute -top-1 -right-1 px-1 min-w-[18px] h-[18px] text-[10px]">
              {contagem > 99 ? '99+' : contagem}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel className="flex justify-between items-center">
          <span>Notificações</span>
          {notificacoes.length > 0 && (
            <Button variant="ghost" size="sm" onClick={marcarTodasComoLidas}>
              Marcar todas como lidas
            </Button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {loading ? (
          <div className="flex justify-center items-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : notificacoes.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground">
            Nenhuma notificação não lida
          </div>
        ) : (
          notificacoes.map((notificacao) => (
            <DropdownMenuItem key={notificacao.id} className="flex flex-col items-start p-3 cursor-default">
              <div className="flex items-start w-full">
                <div className="mr-2 mt-1">
                  {getIconeNotificacao(notificacao.tipo)}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm">{notificacao.titulo}</div>
                  <div className="text-xs text-muted-foreground mt-1">{notificacao.mensagem}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {formatarTempo(notificacao.data_criacao)}
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-6 w-6 ml-2"
                  onClick={() => marcarComoLida(notificacao.id)}
                >
                  <Check className="h-4 w-4" />
                </Button>
              </div>
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}


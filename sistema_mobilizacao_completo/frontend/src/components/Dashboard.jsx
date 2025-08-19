import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  BarChart3, 
  Users, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  TrendingUp,
  Calendar
} from 'lucide-react'
import { dashboardAPI } from '../lib/api'

export default function Dashboard() {
  const [indicadores, setIndicadores] = useState(null)
  const [cardsAtrasados, setCardsAtrasados] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [indicadoresResponse, atrasadosResponse] = await Promise.all([
        dashboardAPI.getIndicadores(),
        dashboardAPI.getCardsAtrasados()
      ])

      if (indicadoresResponse.data.success) {
        setIndicadores(indicadoresResponse.data.data)
      }

      if (atrasadosResponse.data.success) {
        setCardsAtrasados(atrasadosResponse.data.data)
      }
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error)
      setError('Erro ao carregar dados do dashboard')
    } finally {
      setLoading(false)
    }
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
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600">Visão geral do processo de mobilização</p>
      </div>

      {/* Métricas Principais */}
      {indicadores && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Cards</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{indicadores.resumo.total_cards}</div>
              <p className="text-xs text-muted-foreground">
                Colaboradores no sistema
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Em Andamento</CardTitle>
              <Clock className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {indicadores.resumo.cards_em_andamento}
              </div>
              <p className="text-xs text-muted-foreground">
                Processos ativos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Atrasados</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {indicadores.resumo.cards_atrasados}
              </div>
              <p className="text-xs text-muted-foreground">
                Prazos vencidos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Finalizados</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {indicadores.resumo.cards_finalizados}
              </div>
              <p className="text-xs text-muted-foreground">
                Processos completos
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Cards por Etapa */}
      {indicadores && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Cards por Etapa</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {indicadores.por_etapa.map((etapa, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{etapa.etapa}</span>
                    <Badge variant="secondary">{etapa.total}</Badge>
                  </div>
                  <div className="grid grid-cols-4 gap-2 text-sm">
                    <div className="text-center">
                      <div className="text-gray-600">Não Iniciado</div>
                      <div className="font-medium">{etapa.nao_iniciado}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-blue-600">Em Andamento</div>
                      <div className="font-medium">{etapa.em_andamento}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-green-600">Finalizado</div>
                      <div className="font-medium">{etapa.finalizado}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-red-600">Atrasados</div>
                      <div className="font-medium">{etapa.atrasados}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cards Atrasados */}
      {cardsAtrasados.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <span>Cards com Atenção Necessária</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {cardsAtrasados.slice(0, 10).map((card) => (
                <div key={card.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                  <div>
                    <div className="font-medium">{card.nome_colaborador}</div>
                    <div className="text-sm text-gray-600">{card.etapa_atual}</div>
                    <div className="text-sm text-gray-500">{card.responsavel_atual}</div>
                  </div>
                  <div className="text-right">
                    <Badge variant="destructive">
                      {card.status_prazo === 'VENCIDO' ? 'Vencido' : 'Vencendo'}
                    </Badge>
                    <div className="text-xs text-gray-500 mt-1">
                      {card.dias_atraso ? `${card.dias_atraso} dias atrasado` : 
                       card.dias_restantes ? `${card.dias_restantes} dias restantes` : ''}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tempo Médio por Etapa */}
      {indicadores && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Tempo Médio por Etapa</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {indicadores.tempo_medio_etapas.map((etapa, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="font-medium">{etapa.etapa}</span>
                  <div className="text-right">
                    <div className="font-medium">
                      {etapa.tempo_medio_dias} dias (média)
                    </div>
                    <div className="text-sm text-gray-500">
                      Meta: {etapa.prazo_configurado} dias
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}


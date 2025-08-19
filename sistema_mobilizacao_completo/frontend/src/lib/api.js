import axios from 'axios'

// Configuração base da API
const API_BASE_URL = 'http://localhost:5000/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para tratar respostas
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('token')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

// Funções específicas da API
export const authAPI = {
  login: (email, senha) => api.post('/auth/login', { email, senha }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
}

export const cardsAPI = {
  list: (params = {}) => api.get('/cards', { params }),
  get: (id) => api.get(`/cards/${id}`),
  create: (data) => api.post('/cards', data),
  update: (id, data) => api.put(`/cards/${id}`, data),
  move: (id, data) => api.put(`/cards/${id}/mover`, data),
  updateChecklist: (cardId, itemId, data) => api.put(`/cards/${cardId}/checklist/${itemId}`, data),
  delete: (id) => api.delete(`/cards/${id}`),
}

export const etapasAPI = {
  list: () => api.get('/etapas'),
  get: (id) => api.get(`/etapas/${id}`),
  create: (data) => api.post('/etapas', data),
  update: (id, data) => api.put(`/etapas/${id}`, data),
  getChecklist: (id) => api.get(`/etapas/${id}/checklist`),
}

export const usuariosAPI = {
  list: (params = {}) => api.get('/usuarios', { params }),
  get: (id) => api.get(`/usuarios/${id}`),
  create: (data) => api.post('/usuarios', data),
  update: (id, data) => api.put(`/usuarios/${id}`, data),
  delete: (id) => api.delete(`/usuarios/${id}`),
  listGroups: () => api.get('/usuarios/grupos'),
  createGroup: (data) => api.post('/usuarios/grupos', data),
}

export const dashboardAPI = {
  getIndicadores: (params = {}) => api.get('/dashboard/indicadores', { params }),
  getCardsAtrasados: () => api.get('/dashboard/cards-atrasados'),
  getEstatisticasPeriodo: (params = {}) => api.get('/dashboard/estatisticas-periodo', { params }),
}


export const notificacoesAPI = {
  listar: (lidas = false, limite = 50) => {
    return api.get(`/notificacoes?lidas=${lidas}&limite=${limite}`);
  },
  
  contagem: () => {
    return api.get('/notificacoes/contagem');
  },
  
  marcarComoLida: (id) => {
    return api.post(`/notificacoes/${id}/ler`);
  },
  
  marcarTodasComoLidas: () => {
    return api.post('/notificacoes/todas/ler');
  },
  
  verificarPrazos: () => {
    return api.post('/notificacoes/verificar-prazos');
  },
  
  verificarInativos: () => {
    return api.post('/notificacoes/verificar-inativos');
  },
  
  verificarChecklist: () => {
    return api.post('/notificacoes/verificar-checklist');
  },
  
  processarPendentes: () => {
    return api.post('/notificacoes/processar-pendentes');
  },
  
  verificarTudo: () => {
    return api.post('/notificacoes/verificar-tudo');
  }
};


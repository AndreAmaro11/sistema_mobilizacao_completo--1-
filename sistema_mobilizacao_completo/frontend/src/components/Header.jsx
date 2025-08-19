import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu'
import { 
  Search, 
  Filter, 
  Plus, 
  BarChart3, 
  Kanban, 
  User, 
  LogOut,
  Bell
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import NotificacoesDropdown from './NotificacoesDropdown'

export default function Header() {
  const { user, logout } = useAuth()
  const [currentView, setCurrentView] = useState('kanban')

  const handleLogout = () => {
    logout()
  }

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo e Título */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Kanban className="h-8 w-8 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">Sistema de Mobilização</h1>
            </div>
            
            {/* Navegação */}
            <nav className="hidden md:flex space-x-1">
              <Button
                variant={currentView === 'kanban' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setCurrentView('kanban')}
                className="flex items-center space-x-2"
              >
                <Kanban className="h-4 w-4" />
                <span>Kanban</span>
              </Button>
              <Button
                variant={currentView === 'dashboard' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setCurrentView('dashboard')}
                className="flex items-center space-x-2"
              >
                <BarChart3 className="h-4 w-4" />
                <span>Dashboard</span>
              </Button>
            </nav>
          </div>

          {/* Barra de Pesquisa */}
          <div className="flex-1 max-w-md mx-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Pesquisar colaboradores..."
                className="pl-10 pr-4"
              />
            </div>
          </div>

          {/* Ações e Usuário */}
          <div className="flex items-center space-x-4">
            {/* Filtros */}
            <Button variant="outline" size="sm" className="hidden md:flex items-center space-x-2">
              <Filter className="h-4 w-4" />
              <span>Filtros</span>
            </Button>

            {/* Adicionar Card */}
            <Button size="sm" className="flex items-center space-x-2">
              <Plus className="h-4 w-4" />
              <span className="hidden md:inline">Novo Card</span>
            </Button>

            {/* Notificações */}
            <NotificacoesDropdown />

            {/* Menu do Usuário */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="flex items-center space-x-2">
                  <User className="h-4 w-4" />
                  <span className="hidden md:inline">{user?.nome}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <div className="px-2 py-1.5">
                  <p className="text-sm font-medium">{user?.nome}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {user?.grupos?.map((grupo) => (
                      <Badge key={grupo} variant="secondary" className="text-xs">
                        {grupo}
                      </Badge>
                    ))}
                  </div>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />
                  Perfil
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Bell className="mr-2 h-4 w-4" />
                  Notificações
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Sair
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  )
}


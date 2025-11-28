import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { 
  LayoutDashboard, 
  FolderKanban, 
  CheckSquare, 
  PlayCircle, 
  FileText,
  Settings,
  Menu,
  X,
  LogOut,
  User
} from 'lucide-react';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  const [userMenuOpen, setUserMenuOpen] = React.useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Tổng quan' },
    { path: '/projects', icon: FolderKanban, label: 'Dự án' },
    { path: '/tasks', icon: CheckSquare, label: 'Công việc' },
    { path: '/simulations', icon: PlayCircle, label: 'Mô phỏng' },
    { path: '/logs', icon: FileText, label: 'Nhật ký' },
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user?.full_name) return 'U';
    const names = user.full_name.split(' ');
    if (names.length >= 2) {
      return (names[0][0] + names[names.length - 1][0]).toUpperCase();
    }
    return user.full_name[0].toUpperCase();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 fixed w-full top-0 z-10">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <h1 className="text-xl font-bold text-primary-600">
              AI Deadline Forecasting
            </h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
              <Settings size={20} className="text-gray-600" />
            </button>
            
            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-medium">
                  {getUserInitials()}
                </div>
                <span className="text-sm font-medium text-gray-700 hidden md:block">
                  {user?.full_name || 'User'}
                </span>
              </button>

              {/* Dropdown Menu */}
              {userMenuOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setUserMenuOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-20">
                    <div className="px-4 py-3 border-b border-gray-200">
                      <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                      <p className="text-xs text-gray-500 mt-1">{user?.email}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        Vai trò: <span className="font-medium">{user?.role === 'admin' ? 'Quản trị viên' : 'Người dùng'}</span>
                      </p>
                    </div>
                    
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        // Handle profile navigation if needed
                      }}
                      className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      <User size={16} />
                      <span>Thông tin cá nhân</span>
                    </button>
                    
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <LogOut size={16} />
                      <span>Đăng xuất</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white border-r border-gray-200 transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-0 overflow-hidden'
        }`}
      >
        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive(item.path)
                    ? 'bg-primary-50 text-primary-600 font-medium'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main
        className={`pt-16 transition-all duration-300 ${
          sidebarOpen ? 'ml-64' : 'ml-0'
        }`}
      >
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { PlusCircle, Folder, Calendar, CheckCircle, AlertCircle } from 'lucide-react';

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, [statusFilter]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await apiService.getProjects(params);
      setProjects(response.data.projects || []);
      setError(null);
    } catch (err) {
      setError('Không thể tải danh sách dự án. Vui lòng thử lại.');
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      on_hold: 'bg-yellow-100 text-yellow-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status) => {
    const labels = {
      active: 'Đang thực hiện',
      completed: 'Hoàn thành',
      on_hold: 'Tạm dừng',
    };
    return labels[status] || status;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Đang tải...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quản lý Dự án</h1>
          <p className="text-gray-600 mt-1">Danh sách tất cả dự án của bạn</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <PlusCircle size={20} />
          Tạo dự án mới
        </button>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tất cả trạng thái</option>
          <option value="active">Đang thực hiện</option>
          <option value="completed">Hoàn thành</option>
          <option value="on_hold">Tạm dừng</option>
        </select>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <div className="text-center py-12">
          <Folder className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Chưa có dự án nào</h3>
          <p className="mt-1 text-sm text-gray-500">
            Bắt đầu bằng cách tạo một dự án mới.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusCircle className="-ml-1 mr-2 h-5 w-5" />
              Tạo dự án mới
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="block bg-white border rounded-lg hover:shadow-lg transition-shadow p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <Folder className="h-8 w-8 text-blue-600" />
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                  {getStatusLabel(project.status)}
                </span>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2">{project.name}</h3>
              
              {project.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">{project.description}</p>
              )}

              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-500">
                  <Calendar size={16} className="mr-2" />
                  {project.start_date && project.end_date ? (
                    <span>
                      {new Date(project.start_date).toLocaleDateString('vi-VN')} -{' '}
                      {new Date(project.end_date).toLocaleDateString('vi-VN')}
                    </span>
                  ) : (
                    <span>Chưa xác định</span>
                  )}
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">
                    Tasks: {project.completed_tasks}/{project.total_tasks}
                  </span>
                  {project.total_tasks > 0 && (
                    <span className="font-medium text-blue-600">
                      {Math.round((project.completed_tasks / project.total_tasks) * 100)}%
                    </span>
                  )}
                </div>

                {project.total_tasks > 0 && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${(project.completed_tasks / project.total_tasks) * 100}%`,
                      }}
                    />
                  </div>
                )}
              </div>

              {project.owner_name && (
                <div className="mt-4 pt-4 border-t text-sm text-gray-500">
                  Quản lý: {project.owner_name}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}

      {/* Create Project Modal - Simple version */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Tạo dự án mới</h3>
            <p className="text-gray-600 mb-4">
              Form tạo dự án sẽ được triển khai chi tiết sau.
            </p>
            <button
              onClick={() => setShowCreateModal(false)}
              className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
            >
              Đóng
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

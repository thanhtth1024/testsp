import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Activity, CheckCircle, XCircle, Clock, Filter } from 'lucide-react';

export default function AutomationLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [workflowFilter, setWorkflowFilter] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, [statusFilter, workflowFilter]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (workflowFilter) params.workflow_name = workflowFilter;
      
      const response = await apiService.getAutomationLogs(params);
      setLogs(response.data.logs || []);
      setError(null);
    } catch (err) {
      setError('Không thể tải automation logs. Vui lòng thử lại.');
      console.error('Error fetching logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="text-green-600" size={20} />;
      case 'failed':
        return <XCircle className="text-red-600" size={20} />;
      case 'running':
        return <Clock className="text-blue-600 animate-spin" size={20} />;
      default:
        return <Activity className="text-gray-600" size={20} />;
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      success: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      running: 'bg-blue-100 text-blue-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status) => {
    const labels = {
      success: 'Thành công',
      failed: 'Thất bại',
      running: 'Đang chạy',
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
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Automation Logs</h1>
        <p className="text-gray-600 mt-1">
          Lịch sử thực thi các n8n workflows
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tất cả trạng thái</option>
          <option value="success">Thành công</option>
          <option value="failed">Thất bại</option>
          <option value="running">Đang chạy</option>
        </select>

        <input
          type="text"
          value={workflowFilter}
          onChange={(e) => setWorkflowFilter(e.target.value)}
          placeholder="Tìm theo tên workflow..."
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Logs Table */}
      {logs.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border">
          <Activity className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Chưa có log nào</h3>
          <p className="mt-1 text-sm text-gray-500">
            Automation logs sẽ xuất hiện khi các workflow chạy
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Workflow
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trạng thái
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Thời gian
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Chi tiết
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(log.status)}
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">
                          {log.workflow_name}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(log.status)}`}>
                      {getStatusLabel(log.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(log.executed_at).toLocaleString('vi-VN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => setSelectedLog(log)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Xem chi tiết
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Log Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold">Chi tiết Log</h3>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Workflow:</label>
                <p className="text-gray-900">{selectedLog.workflow_name}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Trạng thái:</label>
                <p>
                  <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(selectedLog.status)}`}>
                    {getStatusLabel(selectedLog.status)}
                  </span>
                </p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Thời gian thực thi:</label>
                <p className="text-gray-900">
                  {new Date(selectedLog.executed_at).toLocaleString('vi-VN')}
                </p>
              </div>

              {selectedLog.input_data && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Input Data:</label>
                  <pre className="mt-1 p-3 bg-gray-50 rounded text-xs overflow-auto">
                    {JSON.stringify(selectedLog.input_data, null, 2)}
                  </pre>
                </div>
              )}

              {selectedLog.output_data && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Output Data:</label>
                  <pre className="mt-1 p-3 bg-gray-50 rounded text-xs overflow-auto">
                    {JSON.stringify(selectedLog.output_data, null, 2)}
                  </pre>
                </div>
              )}

              {selectedLog.error_message && (
                <div>
                  <label className="text-sm font-medium text-red-700">Error Message:</label>
                  <p className="mt-1 p-3 bg-red-50 rounded text-sm text-red-700">
                    {selectedLog.error_message}
                  </p>
                </div>
              )}
            </div>

            <div className="mt-6">
              <button
                onClick={() => setSelectedLog(null)}
                className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

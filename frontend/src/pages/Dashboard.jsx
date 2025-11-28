import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react';

const Dashboard = () => {
  const stats = [
    {
      title: 'Dự án',
      value: '5',
      icon: TrendingUp,
      color: 'bg-blue-500',
      change: '+2',
      changeType: 'increase'
    },
    {
      title: 'Công việc',
      value: '15',
      icon: CheckCircle,
      color: 'bg-green-500',
      change: '+5',
      changeType: 'increase'
    },
    {
      title: 'Cảnh báo',
      value: '3',
      icon: AlertTriangle,
      color: 'bg-yellow-500',
      change: '-1',
      changeType: 'decrease'
    },
    {
      title: 'Hoàn thành',
      value: '85%',
      icon: TrendingUp,
      color: 'bg-purple-500',
      change: '+12%',
      changeType: 'increase'
    },
  ];

  const riskTasks = [
    { id: 1, name: 'Tích hợp API Backend', risk: 85, project: 'Website Redesign' },
    { id: 2, name: 'Setup Gemini API integration', risk: 72, project: 'AI Chatbot' },
    { id: 3, name: 'Tích hợp Firebase Authentication', risk: 68, project: 'Mobile App' },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Tổng quan hệ thống</h2>
        <p className="mt-2 text-gray-600">
          Chào mừng trở lại! Đây là bảng điều khiển dự án của bạn.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                  <div className="mt-2 flex items-center text-sm">
                    <span
                      className={`${
                        stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                      } font-medium`}
                    >
                      {stat.change}
                    </span>
                    <span className="ml-2 text-gray-600">so với tháng trước</span>
                  </div>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="text-white" size={24} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Chart Placeholder */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          📊 Biểu đồ tiến độ dự án
        </h3>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <p className="text-gray-500">
            Biểu đồ sẽ được tích hợp với Recharts ở giai đoạn sau
          </p>
        </div>
      </div>

      {/* High Risk Tasks */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            ⚠️ Công việc có nguy cơ trễ cao
          </h3>
          <span className="text-sm text-gray-600">{riskTasks.length} công việc</span>
        </div>
        <div className="space-y-3">
          {riskTasks.map((task) => (
            <div
              key={task.id}
              className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
            >
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{task.name}</h4>
                <p className="text-sm text-gray-600 mt-1">{task.project}</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm text-gray-600">Rủi ro</p>
                  <p className="text-lg font-bold text-red-600">{task.risk}%</p>
                </div>
                <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-500 rounded-full"
                    style={{ width: `${task.risk}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          💡 <strong>Gợi ý:</strong> Hệ thống AI đang phân tích các công việc của bạn mỗi 
          1-2 phút. Các cảnh báo sẽ được gửi tự động khi phát hiện nguy cơ trễ deadline.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;

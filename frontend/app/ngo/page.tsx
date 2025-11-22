"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Users,
  TrendingUp,
  AlertCircle,
  Download,
  CheckCircle,
  XCircle,
  BarChart3,
} from "lucide-react";

export default function NGODashboard() {
  const [stats, setStats] = useState({
    total_verifications: 1250,
    active_workers: 50,
    total_carbon_offset_kg: 680000,
    total_value: 31250,
  });

  const [pendingReviews] = useState([
    {
      id: "VER-001",
      worker_id: "WORKER205",
      trees: 150,
      reason: "Unusually high count",
      date: "2024-01-26",
    },
    {
      id: "VER-002",
      worker_id: "WORKER102",
      trees: 45,
      reason: "Image quality unclear",
      date: "2024-01-26",
    },
    {
      id: "VER-003",
      worker_id: "WORKER089",
      trees: 80,
      reason: "GPS coordinates mismatch",
      date: "2024-01-25",
    },
  ]);

  const [topWorkers] = useState([
    { id: "WORKER012", name: "John Doe", trees: 250, success_rate: 98 },
    { id: "WORKER045", name: "Jane Smith", trees: 180, success_rate: 95 },
    { id: "WORKER101", name: "Bob Jones", trees: 175, success_rate: 100 },
    { id: "WORKER033", name: "Alice Brown", trees: 160, success_rate: 97 },
    { id: "WORKER078", name: "Charlie Davis", trees: 145, success_rate: 96 },
  ]);

  const [recentVerifications] = useState([
    { id: "1", worker: "WORKER012", trees: 25, status: "approved", date: "2 hours ago" },
    { id: "2", worker: "WORKER045", trees: 30, status: "approved", date: "3 hours ago" },
    { id: "3", worker: "WORKER033", trees: 20, status: "approved", date: "5 hours ago" },
    { id: "4", worker: "WORKER078", trees: 150, status: "pending", date: "6 hours ago" },
    { id: "5", worker: "WORKER101", trees: 45, status: "rejected", date: "1 day ago" },
  ]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 text-blue-600">
            <ArrowLeft className="h-5 w-5" />
            <span className="font-semibold">Back to Home</span>
          </Link>
          <div>
            <span className="text-sm text-gray-600">NGO Manager Dashboard</span>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-6">Dashboard Overview</h1>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="flex items-center justify-between mb-2">
                <div className="text-gray-600 text-sm">Verifications</div>
                <BarChart3 className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-blue-600">{stats.total_verifications.toLocaleString()}</div>
              <div className="text-sm text-green-600 mt-2">↑ 12% this month</div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="flex items-center justify-between mb-2">
                <div className="text-gray-600 text-sm">Active Workers</div>
                <Users className="h-5 w-5 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-purple-600">{stats.active_workers}</div>
              <div className="text-sm text-green-600 mt-2">↑ 8% this month</div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="flex items-center justify-between mb-2">
                <div className="text-gray-600 text-sm">CO₂ Offset</div>
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-green-600">
                {(stats.total_carbon_offset_kg / 1000).toFixed(0)} tons
              </div>
              <div className="text-sm text-green-600 mt-2">↑ 15% this month</div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="flex items-center justify-between mb-2">
                <div className="text-gray-600 text-sm">Total Value</div>
                <TrendingUp className="h-5 w-5 text-orange-600" />
              </div>
              <div className="text-3xl font-bold text-orange-600">
                ${stats.total_value.toLocaleString()}
              </div>
              <div className="text-sm text-green-600 mt-2">↑ 18% this month</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Pending Reviews & Top Workers */}
          <div className="lg:col-span-2 space-y-8">
            {/* Pending Reviews */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <AlertCircle className="h-6 w-6 text-orange-600" />
                  Pending Reviews ({pendingReviews.length})
                </h2>
              </div>

              <div className="space-y-4">
                {pendingReviews.map((review) => (
                  <div key={review.id} className="border rounded-lg p-4 hover:shadow-md transition">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="font-semibold">{review.worker_id}</div>
                        <div className="text-sm text-gray-600">
                          {review.trees} trees • {review.date}
                        </div>
                      </div>
                      <span className="px-3 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">
                        {review.reason}
                      </span>
                    </div>
                    <div className="flex gap-2 mt-3">
                      <button className="flex-1 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition text-sm font-medium">
                        Review Details
                      </button>
                      <button className="flex-1 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium">
                        Approve
                      </button>
                      <button className="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm font-medium">
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Verifications */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold mb-6">Recent Verifications</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                        Worker
                      </th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                        Trees
                      </th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                        Status
                      </th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                        Time
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentVerifications.map((ver) => (
                      <tr key={ver.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium">{ver.worker}</td>
                        <td className="py-3 px-4">{ver.trees}</td>
                        <td className="py-3 px-4">
                          {ver.status === "approved" && (
                            <span className="flex items-center gap-1 text-green-600">
                              <CheckCircle className="h-4 w-4" />
                              Approved
                            </span>
                          )}
                          {ver.status === "pending" && (
                            <span className="flex items-center gap-1 text-orange-600">
                              <AlertCircle className="h-4 w-4" />
                              Pending
                            </span>
                          )}
                          {ver.status === "rejected" && (
                            <span className="flex items-center gap-1 text-red-600">
                              <XCircle className="h-4 w-4" />
                              Rejected
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-gray-600 text-sm">{ver.date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right Column - Top Workers & Actions */}
          <div className="space-y-8">
            {/* Top Workers */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold mb-6">Top Performers</h2>
              <div className="space-y-4">
                {topWorkers.map((worker, index) => (
                  <div
                    key={worker.id}
                    className="flex items-center gap-4 p-3 border rounded-lg hover:shadow-md transition"
                  >
                    <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-green-600 text-white rounded-full flex items-center justify-center font-bold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold">{worker.name}</div>
                      <div className="text-sm text-gray-600">
                        {worker.trees} trees • {worker.success_rate}% success
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold mb-6">Quick Actions</h2>
              <div className="space-y-3">
                <button className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2">
                  <Download className="h-5 w-5" />
                  Generate Report
                </button>
                <button className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center justify-center gap-2">
                  <Users className="h-5 w-5" />
                  Manage Workers
                </button>
                <button className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center justify-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  View Analytics
                </button>
              </div>
            </div>

            {/* System Health */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold mb-4">System Health</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">API Status</span>
                  <span className="flex items-center gap-1 text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    Online
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Blockchain</span>
                  <span className="flex items-center gap-1 text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    Connected
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">AI Validator</span>
                  <span className="flex items-center gap-1 text-orange-600">
                    <AlertCircle className="h-4 w-4" />
                    Mock Mode
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

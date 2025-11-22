"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Search,
  Filter,
  MapPin,
  Calendar,
  CheckCircle2,
  ShoppingCart,
  TrendingUp,
  BarChart3,
  Download,
} from "lucide-react";

export default function CorporateMarketplace() {
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null);

  const [batches] = useState([
    {
      id: "BATCH-001",
      name: "Mumbai Reforestation Project",
      trees: 1000,
      carbon_kg: 21770,
      location: "Mumbai, Maharashtra, India",
      verified: ["Satellite", "AI", "GPS"],
      price_per_tree: 1.0,
      date: "January 2024",
      confidence: 98,
      ngo: "Green India Foundation",
    },
    {
      id: "BATCH-002",
      name: "Bangalore Urban Forest",
      trees: 500,
      carbon_kg: 10885,
      location: "Bangalore, Karnataka, India",
      verified: ["AI", "GPS", "Weather"],
      price_per_tree: 0.9,
      date: "January 2024",
      confidence: 95,
      ngo: "Urban Forest Initiative",
    },
    {
      id: "BATCH-003",
      name: "Delhi NCR Green Belt",
      trees: 750,
      carbon_kg: 16328,
      location: "Delhi, NCR, India",
      verified: ["Satellite", "AI", "GPS", "Weather"],
      price_per_tree: 1.1,
      date: "December 2023",
      confidence: 99,
      ngo: "Delhi Green Corps",
    },
  ]);

  const [portfolio] = useState({
    total_credits: 2500,
    total_carbon_kg: 54425,
    total_value: 62500,
    nfts_owned: 100,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 text-purple-600">
            <ArrowLeft className="h-5 w-5" />
            <span className="font-semibold">Back to Home</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="#portfolio" className="text-gray-600 hover:text-gray-900 transition">
              My Portfolio
            </Link>
            <Link
              href="#esg"
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              ESG Report
            </Link>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* Portfolio Summary */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-6">Carbon Credit Marketplace</h1>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-gradient-to-br from-green-500 to-emerald-600 text-white p-6 rounded-xl shadow-md">
              <div className="text-sm opacity-90 mb-2">Your Carbon Offset Goal</div>
              <div className="text-3xl font-bold mb-2">50 tons/month</div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-white/30 rounded-full overflow-hidden">
                  <div className="h-full bg-white rounded-full" style={{ width: "68%" }} />
                </div>
                <span className="text-sm">68%</span>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="text-gray-600 text-sm mb-2">Total Credits</div>
              <div className="text-3xl font-bold text-purple-600">
                {portfolio.total_credits.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500 mt-2">
                {(portfolio.total_carbon_kg / 1000).toFixed(1)} tons CO₂
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="text-gray-600 text-sm mb-2">Investment</div>
              <div className="text-3xl font-bold text-blue-600">
                ${portfolio.total_value.toLocaleString()}
              </div>
              <div className="text-sm text-green-600 mt-2">↑ 12% this quarter</div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="text-gray-600 text-sm mb-2">NFTs Owned</div>
              <div className="text-3xl font-bold text-orange-600">{portfolio.nfts_owned}</div>
              <div className="text-sm text-gray-500 mt-2">Blockchain verified</div>
            </div>
          </div>
        </div>

        {/* Search & Filter */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search projects..."
                className="w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>
            <button className="px-6 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Filters
            </button>
            <select className="px-6 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 outline-none">
              <option>Sort: Price (Low to High)</option>
              <option>Sort: Price (High to Low)</option>
              <option>Sort: Newest First</option>
              <option>Sort: Most Verified</option>
            </select>
          </div>
        </div>

        {/* Available Batches */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {batches.map((batch) => (
            <div
              key={batch.id}
              className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition cursor-pointer"
              onClick={() => setSelectedBatch(batch.id)}
            >
              <div className="h-48 bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-white">
                <div className="text-center">
                  <div className="text-6xl font-bold mb-2">{batch.trees}</div>
                  <div className="text-xl">Trees Planted</div>
                </div>
              </div>

              <div className="p-6">
                <h3 className="text-2xl font-bold mb-3">{batch.name}</h3>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="h-4 w-4" />
                    <span className="text-sm">{batch.location}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Calendar className="h-4 w-4" />
                    <span className="text-sm">{batch.date}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <TrendingUp className="h-4 w-4" />
                    <span className="text-sm">{batch.carbon_kg.toLocaleString()} kg CO₂</span>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="text-sm text-gray-600 mb-2">Verification Methods:</div>
                  <div className="flex flex-wrap gap-2">
                    {batch.verified.map((method) => (
                      <span
                        key={method}
                        className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium flex items-center gap-1"
                      >
                        <CheckCircle2 className="h-3 w-3" />
                        {method}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Confidence Score</span>
                    <span className="text-sm font-semibold text-green-600">{batch.confidence}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-600 rounded-full"
                      style={{ width: `${batch.confidence}%` }}
                    />
                  </div>
                </div>

                <div className="border-t pt-4 flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-600">Price</div>
                    <div className="text-2xl font-bold text-purple-600">
                      ${(batch.trees * batch.price_per_tree).toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-500">${batch.price_per_tree}/tree</div>
                  </div>
                  <button className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center gap-2">
                    <ShoppingCart className="h-5 w-5" />
                    Purchase
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* ESG Report Preview */}
        <div className="bg-gradient-to-br from-purple-600 to-pink-600 text-white rounded-2xl p-8">
          <div className="max-w-3xl mx-auto text-center">
            <BarChart3 className="h-16 w-16 mx-auto mb-4 opacity-90" />
            <h2 className="text-3xl font-bold mb-4">Generate ESG Compliance Report</h2>
            <p className="text-purple-100 mb-6">
              Download a comprehensive report for stakeholders showing your carbon offset
              achievements, blockchain-verified credits, and environmental impact metrics.
            </p>
            <button className="px-8 py-4 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition flex items-center gap-2 mx-auto">
              <Download className="h-5 w-5" />
              Generate Report (PDF)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import Link from "next/link";
import { Trees, Building2, Users, Leaf, Shield, Coins } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Hero Section */}
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Leaf className="h-8 w-8 text-green-600" />
            <span className="text-2xl font-bold text-green-800">CarbonChain</span>
          </div>
          <div className="flex gap-4">
            <Link
              href="/worker"
              className="px-4 py-2 text-green-700 hover:text-green-900 font-medium transition"
            >
              Worker Portal
            </Link>
            <Link
              href="/ngo"
              className="px-4 py-2 text-green-700 hover:text-green-900 font-medium transition"
            >
              NGO Dashboard
            </Link>
            <Link
              href="/corporate"
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              Buy Credits
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-6">
          Verify Carbon Credits with
          <span className="text-green-600"> Blockchain</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          AI-powered, biometric-verified, satellite-confirmed tree planting. Every carbon credit is
          an NFT on Algorand blockchain with irrefutable proof.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/worker"
            className="px-8 py-4 bg-green-600 text-white rounded-lg font-semibold text-lg hover:bg-green-700 transition shadow-lg"
          >
            Start Verifying
          </Link>
          <Link
            href="/corporate"
            className="px-8 py-4 bg-white text-green-600 border-2 border-green-600 rounded-lg font-semibold text-lg hover:bg-green-50 transition"
          >
            Buy Credits
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mt-20">
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-4xl font-bold text-green-600 mb-2">1.2M+</div>
            <div className="text-gray-600">Trees Verified</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-4xl font-bold text-green-600 mb-2">26K</div>
            <div className="text-gray-600">Tons CO₂ Offset</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-4xl font-bold text-green-600 mb-2">95%</div>
            <div className="text-gray-600">Fraud Detection</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-4xl font-bold text-green-600 mb-2">5K+</div>
            <div className="text-gray-600">Active Workers</div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-white py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 border rounded-xl hover:shadow-lg transition">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <Trees className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Plant & Capture</h3>
              <p className="text-gray-600">
                Workers plant trees and capture proof with gesture biometrics and GPS location.
              </p>
            </div>

            <div className="p-8 border rounded-xl hover:shadow-lg transition">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <Shield className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold mb-3">AI Verification</h3>
              <p className="text-gray-600">
                6-layer validation: gestures, GPS, weather, AI fraud detection, image analysis, and
                satellite confirmation.
              </p>
            </div>

            <div className="p-8 border rounded-xl hover:shadow-lg transition">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                <Coins className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Mint NFT</h3>
              <p className="text-gray-600">
                Verified credits become tradeable NFTs on Algorand blockchain with immutable proof.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* User Types */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-12">Choose Your Portal</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Link
              href="/worker"
              className="group p-8 bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-2xl hover:shadow-2xl transition-all transform hover:-translate-y-2"
            >
              <Users className="h-12 w-12 mb-4" />
              <h3 className="text-3xl font-bold mb-3">Field Workers</h3>
              <p className="text-green-50 mb-4">
                Verify your tree planting work and earn carbon credit NFTs instantly.
              </p>
              <div className="text-green-100 group-hover:text-white transition">
                Start Verification →
              </div>
            </Link>

            <Link
              href="/ngo"
              className="group p-8 bg-gradient-to-br from-blue-500 to-cyan-600 text-white rounded-2xl hover:shadow-2xl transition-all transform hover:-translate-y-2"
            >
              <Building2 className="h-12 w-12 mb-4" />
              <h3 className="text-3xl font-bold mb-3">NGO Managers</h3>
              <p className="text-blue-50 mb-4">
                Monitor workers, review verifications, and generate reports for donors.
              </p>
              <div className="text-blue-100 group-hover:text-white transition">
                Open Dashboard →
              </div>
            </Link>

            <Link
              href="/corporate"
              className="group p-8 bg-gradient-to-br from-purple-500 to-pink-600 text-white rounded-2xl hover:shadow-2xl transition-all transform hover:-translate-y-2"
            >
              <Coins className="h-12 w-12 mb-4" />
              <h3 className="text-3xl font-bold mb-3">Corporations</h3>
              <p className="text-purple-50 mb-4">
                Purchase verified carbon credits and generate ESG compliance reports.
              </p>
              <div className="text-purple-100 group-hover:text-white transition">
                Browse Marketplace →
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Leaf className="h-6 w-6" />
            <span className="text-xl font-bold">CarbonChain</span>
          </div>
          <p className="text-gray-400 mb-4">
            Blockchain-verified carbon credits for a sustainable future
          </p>
          <div className="flex justify-center gap-6 text-sm text-gray-400">
            <a href="#" className="hover:text-white transition">
              About
            </a>
            <a href="#" className="hover:text-white transition">
              Docs
            </a>
            <a href="#" className="hover:text-white transition">
              API
            </a>
            <a href="#" className="hover:text-white transition">
              Contact
            </a>
          </div>
          <p className="text-gray-500 text-sm mt-6">
            Built with 🌱 for a sustainable future | Powered by Algorand
          </p>
        </div>
      </footer>
    </div>
  );
}

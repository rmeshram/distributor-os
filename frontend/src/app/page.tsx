"use client";

import React from "react";
import Link from "next/link";
import { MessageSquare, Map, Database, ArrowRight, Check, Sparkles, Truck, Box } from "lucide-react";

export default function MarketingPage() {
  return (
    <div className="bg-slate-50 min-h-screen text-slate-800 font-sans selection:bg-blue-100">
      
      {/* 1. Header Navigation */}
      <header className="border-b border-slate-100 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white text-base font-black shadow-md shadow-blue-200">
              D
            </div>
            <span className="font-extrabold text-slate-800 text-lg tracking-tight">Distributor OS</span>
          </div>

          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-xs font-bold text-slate-500 hover:text-slate-800 transition-colors uppercase tracking-wider">Features</a>
            <a href="#pricing" className="text-xs font-bold text-slate-500 hover:text-slate-800 transition-colors uppercase tracking-wider">Pricing</a>
            <a href="#about" className="text-xs font-bold text-slate-500 hover:text-slate-800 transition-colors uppercase tracking-wider">Solutions</a>
          </nav>

          <div className="flex items-center gap-4">
            <Link 
              href="/auth" 
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-blue-100 flex items-center gap-1.5 cursor-pointer"
            >
              <span>Launch 15-Day Free Trial</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* 2. Hero Section */}
      <section className="py-20 px-6 max-w-7xl mx-auto text-center relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-100/30 rounded-full blur-3xl -z-10 animate-pulse" />
        
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-blue-50 border border-blue-100/50 rounded-full text-blue-700 text-[11px] font-bold uppercase tracking-wider mb-6">
          <Sparkles className="w-3.5 h-3.5 animate-spin-slow text-blue-500" />
          <span>Next-Generation Supply Chain Cockpit</span>
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-slate-900 tracking-tight max-w-4xl mx-auto leading-[1.1]">
          Modern Operations Control Center for <span className="text-blue-600">B2B Distributors</span>
        </h1>
        
        <p className="text-sm sm:text-base text-slate-500 max-w-2xl mx-auto mt-6 leading-relaxed font-semibold">
          Ingest unstructured WhatsApp orders instantly with AI, allocate optimization route delivery sheets to driver terminals, and monitor warehouse stock levels.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link 
            href="/auth" 
            className="w-full sm:w-auto px-8 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-sm transition-all shadow-lg shadow-blue-100 flex items-center justify-center gap-2 cursor-pointer"
          >
            <span>Launch Free Trial</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <a 
            href="#features" 
            className="w-full sm:w-auto px-8 py-3.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 font-bold rounded-xl text-sm transition-all shadow-sm flex items-center justify-center gap-1.5"
          >
            Explore Features
          </a>
        </div>
      </section>

      {/* 3. Features Grid */}
      <section id="features" className="py-20 px-6 max-w-7xl mx-auto border-t border-slate-100">
        <div className="text-center max-w-xl mx-auto mb-16">
          <h2 className="text-2xl sm:text-3xl font-black text-slate-800 tracking-tight">Supercharged features built for scale</h2>
          <p className="text-xs text-slate-400 font-bold mt-2 uppercase tracking-widest">Core Capabilities</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Card 1 */}
          <div className="bg-white border border-slate-100 rounded-2xl p-8 shadow-sm hover:shadow-md transition-all flex flex-col justify-between h-[300px]">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-sm">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">WhatsApp AI Ingestion</h3>
              <p className="text-xs text-slate-500 font-semibold leading-relaxed">
                Automatically parse unstructured Hinglish message streams or audio memos into canonical draft digital orders. Gemini AI maps products, quantities, and customer profile details.
              </p>
            </div>
          </div>

          {/* Card 2 */}
          <div className="bg-white border border-slate-100 rounded-2xl p-8 shadow-sm hover:shadow-md transition-all flex flex-col justify-between h-[300px]">
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-sm">
              <Map className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">Real-Time Route Sheets</h3>
              <p className="text-xs text-slate-500 font-semibold leading-relaxed">
                Compile unallocated confirmed invoice checkpoints into optimal transport run sheets. Track drivers, vehicle assignments, and milestone delivery completions instantly.
              </p>
            </div>
          </div>

          {/* Card 3 */}
          <div className="bg-white border border-slate-100 rounded-2xl p-8 shadow-sm hover:shadow-md transition-all flex flex-col justify-between h-[300px]">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shadow-sm">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">Digital Stock Ledger</h3>
              <p className="text-xs text-slate-500 font-semibold leading-relaxed">
                Strict inequality low-stock bounds prevent fulfillment lockups. Maintain a clean ledger mapping real warehouse location bins, threshold counts, and Tally/Marg ERP catalog sync.
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* 4. Pricing Matrices */}
      <section id="pricing" className="py-20 px-6 max-w-7xl mx-auto border-t border-slate-100 bg-slate-50">
        <div className="text-center max-w-xl mx-auto mb-16">
          <h2 className="text-2xl sm:text-3xl font-black text-slate-800 tracking-tight">Simple, transparent, self-service pricing</h2>
          <p className="text-xs text-slate-400 font-bold mt-2 uppercase tracking-widest">pricing matrices</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Tier 1 */}
          <div className="bg-white border border-slate-150 rounded-2xl p-8 shadow-sm flex flex-col justify-between min-h-[420px]">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400">Starter</span>
              <h3 className="text-xl font-bold text-slate-800 mt-1">Micro Warehousing</h3>
              <div className="mt-4 flex items-baseline gap-1 text-slate-800">
                <span className="text-3xl font-extrabold">₹4,999</span>
                <span className="text-xs text-slate-400 font-semibold">/month</span>
              </div>
              <p className="text-xs text-slate-500 font-semibold mt-3">Essential tools for single-warehouse local distributors.</p>
              
              <ul className="mt-6 space-y-3">
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>1 Warehouse & Location Track</span>
                </li>
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>100 AI Ingestions / month</span>
                </li>
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Standard Route Sheet Exports</span>
                </li>
              </ul>
            </div>
            
            <Link href="/auth" className="mt-8 w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs text-center transition-all cursor-pointer block">
              Get Started
            </Link>
          </div>

          {/* Tier 2 */}
          <div className="bg-white border-2 border-blue-500 rounded-2xl p-8 shadow-md flex flex-col justify-between min-h-[420px] relative">
            <div className="absolute top-0 right-6 -translate-y-1/2 bg-blue-500 text-white text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded-full">
              Most Popular
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-blue-500">Growth</span>
              <h3 className="text-xl font-bold text-slate-800 mt-1">Professional Fleet</h3>
              <div className="mt-4 flex items-baseline gap-1 text-slate-800">
                <span className="text-3xl font-extrabold">₹9,999</span>
                <span className="text-xs text-slate-400 font-semibold">/month</span>
              </div>
              <p className="text-xs text-slate-500 font-semibold mt-3">Complete operational cockpit for mid-size distributor networks.</p>
              
              <ul className="mt-6 space-y-3">
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>3 Warehouses & Bin Control</span>
                </li>
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Unlimited AI Ingestions & Webhooks</span>
                </li>
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Live Driver Optimization Run Sheets</span>
                </li>
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>FIFO Collection Allocation & Ledgers</span>
                </li>
              </ul>
            </div>
            
            <Link href="/auth" className="mt-8 w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-xs text-center transition-all shadow-md shadow-blue-100 cursor-pointer block">
              Launch 15-Day Free Trial
            </Link>
          </div>

          {/* Tier 3 */}
          <div className="bg-white border border-slate-150 rounded-2xl p-8 shadow-sm flex flex-col justify-between min-h-[420px]">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400">Enterprise</span>
              <h3 className="text-xl font-bold text-slate-800 mt-1">Industrial ERP</h3>
              <div className="mt-4 flex items-baseline gap-1 text-slate-800">
                <span className="text-3xl font-extrabold">Custom</span>
              </div>
              <p className="text-xs text-slate-500 font-semibold mt-3">High-volume deployment with custom database integrations.</p>
              
              <ul className="mt-6 space-y-3">
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Unlimited Warehouses</span>
                </li>
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Custom CRM/ODBC Tally integrations</span>
                </li>
                <li className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Dedicated Server Instance & SLA</span>
                </li>
              </ul>
            </div>
            
            <button className="mt-8 w-full py-2.5 bg-slate-850 hover:bg-slate-950 text-white font-bold rounded-xl text-xs text-center transition-all cursor-pointer">
              Contact Sales
            </button>
          </div>

        </div>
      </section>

      {/* 5. Footer */}
      <footer className="border-t border-slate-100 bg-white py-12 px-6 text-center">
        <p className="text-[11px] text-slate-400 font-semibold">
          © 2026 Distributor OS. All rights reserved. Supply chain control pipelines engineered for modern distributors.
        </p>
      </footer>

    </div>
  );
}

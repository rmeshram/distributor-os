"use client";

import React, { useState } from "react";
import { Truck, MapPin, Navigation, Info, ArrowRight } from "lucide-react";

interface DeliveryMarker {
  id: string;
  vehicle: string;
  carrier: string;
  tracking_id: string;
  status: string;
  location: string;
  x: number; // percentage
  y: number; // percentage
}

export default function LiveDeliveries() {
  const [activeMarker, setActiveMarker] = useState<DeliveryMarker | null>(null);

  const deliveries: DeliveryMarker[] = [
    { id: "1", vehicle: "KA01 AB 1234", carrier: "Delhivery", tracking_id: "DELH982738472", status: "On the way", location: "Malleshwaram", x: 30, y: 35 },
    { id: "2", vehicle: "KA02 EF 9012", carrier: "Blue Dart", tracking_id: "BD2983749", status: "Delivered", location: "Whitefield", x: 75, y: 55 },
    { id: "3", vehicle: "KA03 CD 5678", carrier: "Delhivery", tracking_id: "DELH129384729", status: "On the way", location: "HSR Layout", x: 45, y: 80 },
    { id: "4", vehicle: "KA05 GH 3456", carrier: "Blue Dart", tracking_id: "BD4837261", status: "On the way", location: "Indiranagar", x: 65, y: 45 }
  ];

  return (
    <div className="bg-white p-5 rounded-xl border border-dashboard-border shadow-sm flex flex-col justify-between h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-dashboard-border mb-3">
        <div className="flex items-center gap-2">
          <h3 className="font-bold text-slate-800 text-base">Live Deliveries</h3>
          <span className="flex h-2.5 w-2.5 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-semibold text-emerald-600">Live</span>
        </div>
        <button className="text-xs font-semibold text-brand-blue hover:text-brand-blueHover hover:underline flex items-center gap-1">
          <span>View all deliveries</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Interactive Map Canvas */}
      <div className="relative flex-1 bg-slate-50 border border-slate-200 rounded-xl overflow-hidden min-h-[220px]">
        {/* Mock Map Background grid lines & streets */}
        <svg className="absolute inset-0 w-full h-full text-slate-200" xmlns="http://www.w3.org/2000/svg">
          {/* Main roads */}
          <path d="M 0 50 Q 150 120, 300 100 T 500 180" fill="none" stroke="currentColor" strokeWidth="8" strokeOpacity="0.4" />
          <path d="M 100 0 C 120 100, 180 200, 150 300" fill="none" stroke="currentColor" strokeWidth="6" strokeOpacity="0.4" />
          <path d="M 350 0 C 300 100, 250 200, 300 300" fill="none" stroke="currentColor" strokeWidth="6" strokeOpacity="0.4" />
          <path d="M 0 200 C 150 180, 250 220, 500 120" fill="none" stroke="currentColor" strokeWidth="8" strokeOpacity="0.4" />
          
          {/* Inner ring road circle */}
          <circle cx="230" cy="130" r="80" fill="none" stroke="currentColor" strokeWidth="4" strokeDasharray="5,5" strokeOpacity="0.5" />
          
          {/* Grid lines */}
          <line x1="0" y1="50" x2="500" y2="50" stroke="currentColor" strokeWidth="0.5" strokeOpacity="0.2" />
          <line x1="0" y1="150" x2="500" y2="150" stroke="currentColor" strokeWidth="0.5" strokeOpacity="0.2" />
          <line x1="0" y1="250" x2="500" y2="250" stroke="currentColor" strokeWidth="0.5" strokeOpacity="0.2" />
          <line x1="100" y1="0" x2="100" y2="300" stroke="currentColor" strokeWidth="0.5" strokeOpacity="0.2" />
          <line x1="250" y1="0" x2="250" y2="300" stroke="currentColor" strokeWidth="0.5" strokeOpacity="0.2" />
          <line x1="400" y1="0" x2="400" y2="300" stroke="currentColor" strokeWidth="0.5" strokeOpacity="0.2" />
        </svg>

        {/* Labels for landmarks */}
        <span className="absolute text-[10px] text-slate-400 font-bold tracking-widest top-4 left-6">MALLESHWARAM</span>
        <span className="absolute text-[10px] text-slate-400 font-bold tracking-widest top-6 right-8">WHITEFIELD</span>
        <span className="absolute text-[10px] text-slate-400 font-bold tracking-widest bottom-6 left-12">HSR LAYOUT</span>
        <span className="absolute text-[11px] text-slate-600 font-bold bottom-1/2 left-1/3 -translate-x-1/2">Bengaluru</span>

        {/* Vehicle Markers */}
        {deliveries.map((marker) => {
          const isActive = activeMarker?.id === marker.id;
          return (
            <div
              key={marker.id}
              className="absolute"
              style={{ left: `${marker.x}%`, top: `${marker.y}%` }}
            >
              {/* Pin marker */}
              <button
                onClick={() => setActiveMarker(isActive ? null : marker)}
                className={`w-8 h-8 -translate-x-1/2 -translate-y-1/2 rounded-full flex items-center justify-center border-2 shadow-lg transition-all ${
                  marker.status === "Delivered"
                    ? "bg-emerald-500 border-white text-white hover:bg-emerald-600"
                    : "bg-brand-blue border-white text-white hover:bg-brand-blueHover"
                } ${isActive ? "scale-125 ring-4 ring-brand-blue/30" : ""}`}
              >
                <Truck className="w-4.5 h-4.5" />
              </button>

              {/* Tooltip Overlay */}
              {isActive && (
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] p-2.5 rounded-xl shadow-xl w-44 z-30 flex flex-col gap-1 border border-slate-700 animate-fade-in">
                  <div className="flex items-center justify-between border-b border-slate-700 pb-1 mb-1">
                    <span className="font-bold">{marker.vehicle}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold ${
                      marker.status === "Delivered" ? "bg-emerald-500/20 text-emerald-400" : "bg-blue-500/20 text-blue-400"
                    }`}>
                      {marker.status}
                    </span>
                  </div>
                  <p className="text-slate-300 font-medium">Carrier: {marker.carrier}</p>
                  <p className="text-slate-300 font-medium truncate">Tracking: {marker.tracking_id}</p>
                  <p className="text-slate-300 font-medium">Location: {marker.location}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

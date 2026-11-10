import React, { useState, useEffect } from 'react';
import {
  MapPin, Navigation, ShieldAlert, CheckCircle2, DollarSign,
  Dumbbell, ShoppingCart, Fuel, Cpu, Globe, ShieldCheck, ArrowRight, Ban
} from 'lucide-react';
import { api } from '../services/api';
import { ProductItem } from '../types';

interface NearbySavingsProps {
  activeUserId: string;
  onSelectForCheckout?: (product: ProductItem) => void;
}

export const NearbySavings: React.FC<NearbySavingsProps> = ({
  activeUserId = 'usr_alex_chen',
  onSelectForCheckout
}) => {
  const [locStatus, setLocStatus] = useState<any>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('fitness');
  const [alternatives, setAlternatives] = useState<any[]>([]);
  const [gymScenario, setGymScenario] = useState<any>(null);
  const [liveOsmResult, setLiveOsmResult] = useState<any>(null);
  const [loadingOsm, setLoadingOsm] = useState(false);
  const [gpsMessage, setGpsMessage] = useState<string | null>(null);

  // Manual location override state
  const [manualCity, setManualCity] = useState('San Francisco');
  const [manualLat, setManualLat] = useState('37.7749');
  const [manualLon, setManualLon] = useState('-122.4194');

  const loadData = async (cat: string = selectedCategory) => {
    try {
      const [status, near, gym] = await Promise.all([
        api.getLocationStatus(activeUserId),
        api.discoverNearbyPlaces(cat, activeUserId, 15.0),
        api.getGymScenario(activeUserId)
      ]);
      setLocStatus(status);
      setAlternatives(near || []);
      setGymScenario(gym);
    } catch (err) {
      console.error('Error loading nearby savings intelligence:', err);
    }
  };

  useEffect(() => {
    loadData(selectedCategory);
  }, [activeUserId, selectedCategory]);

  const handleRequestBrowserGps = () => {
    setGpsMessage('Requesting one-time browser geolocation permission...');
    if (!navigator.geolocation) {
      setGpsMessage('Browser Geolocation API is not supported in this browser. Use Manual Location below.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        setManualLat(lat.toFixed(4));
        setManualLon(lon.toFixed(4));
        await api.updateLocationPermission({
          user_id: activeUserId,
          is_granted: true,
          precision_mode: 'precise',
          access_type: 'one_time',
          latitude: lat,
          longitude: lon,
          city: `Permitted Browser GPS (${lat.toFixed(3)}, ${lon.toFixed(3)})`,
          location_source: 'browser_gps'
        });
        setGpsMessage(`Browser GPS authorized (One-time fix: ${lat.toFixed(4)}, ${lon.toFixed(4)}). Zero background tracking.`);
        await loadData(selectedCategory);
      },
      async (err) => {
        setGpsMessage(`Browser GPS permission denied or unavailable (${err.message}). Using safe manual/fallback mode.`);
        await api.updateLocationPermission({
          user_id: activeUserId,
          is_granted: false,
          precision_mode: 'disabled',
          access_type: 'disabled'
        });
        await loadData(selectedCategory);
      },
      { enableHighAccuracy: false, timeout: 8000 }
    );
  };

  const handleManualLocationUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    const lat = parseFloat(manualLat) || 37.7749;
    const lon = parseFloat(manualLon) || -122.4194;
    await api.updateLocationPermission({
      user_id: activeUserId,
      is_granted: true,
      precision_mode: 'approximate',
      access_type: 'one_time',
      latitude: lat,
      longitude: lon,
      city: manualCity || 'Manual Location',
      location_source: 'manual_selection'
    });
    setGpsMessage(`Manual location set to ${manualCity} (${lat.toFixed(4)}, ${lon.toFixed(4)}).`);
    await loadData(selectedCategory);
  };

  const handleStopLocationAccess = async () => {
    await api.updateLocationPermission({
      user_id: activeUserId,
      is_granted: false,
      precision_mode: 'disabled',
      access_type: 'disabled'
    });
    setGpsMessage('Location access revoked and cleared. FINORA is not accessing your coordinates.');
    setLiveOsmResult(null);
    await loadData(selectedCategory);
  };

  const handleQueryLiveOsm = async () => {
    if (!locStatus?.is_granted) {
      setGpsMessage('Please grant location permission or set a manual location before querying OpenStreetMap.');
      return;
    }
    setLoadingOsm(true);
    try {
      const lat = locStatus.latitude || parseFloat(manualLat) || 37.7749;
      const lon = locStatus.longitude || parseFloat(manualLon) || -122.4194;
      const res = await api.discoverLiveOsmPlaces(lat, lon, selectedCategory, 3500);
      setLiveOsmResult(res);
    } catch (err) {
      console.error('OSM query failed:', err);
    } finally {
      setLoadingOsm(false);
    }
  };

  const handleCheckoutSwitch = (planId: string, name: string, price: number) => {
    if (!onSelectForCheckout) return;
    onSelectForCheckout({
      product_id: planId,
      product_name: name,
      category: 'subscriptions',
      merchant_id: 'm_verified_partner',
      price: price,
      shipping_cost: 0,
      total_cost: price,
      currency: 'USD',
      availability: true,
      rating: 4.9,
      review_count: 420,
      delivery_days: 0,
      warranty_months: 12,
      specifications: { plan_type: 'Money-Saving Switch' },
      description: 'User-approved money-saving plan switch executed in PayPal Sandbox.'
    });
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            GPS & Nearby Places Money-Saving Intelligence
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Permission-first location discovery, transport-adjusted price comparison & gym underutilization analysis
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={handleRequestBrowserGps}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20"
          >
            <Navigation className="w-3.5 h-3.5" />
            Use Browser GPS (One-Time)
          </button>

          {locStatus?.is_granted && (
            <button
              onClick={handleStopLocationAccess}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 font-semibold text-xs"
            >
              <Ban className="w-3.5 h-3.5" />
              Stop Location Access
            </button>
          )}
        </div>
      </div>

      {/* Location Permission & Manual Control Banner */}
      <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
        <div className="lg:col-span-6 space-y-1">
          <div className="flex items-center gap-2">
            <MapPin className={`w-4 h-4 ${locStatus?.is_granted ? 'text-emerald-400' : 'text-amber-400'}`} />
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Location Status: {locStatus?.is_granted ? 'Authorized (One-Time Fix)' : 'Permission Disabled / Revoked'}
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-cyan-400 border border-slate-700">
              Source: {locStatus?.location_source || 'none'}
            </span>
          </div>
          <p className="text-xs text-slate-400">
            {locStatus?.is_granted
              ? `Active Reference: ${locStatus.city} (${Number(locStatus.latitude).toFixed(4)}, ${Number(locStatus.longitude).toFixed(4)})`
              : 'Location access is off. You can select a manual city below or use clearly labelled demo benchmarks.'}
          </p>
          {gpsMessage && (
            <p className="text-[11px] text-cyan-300 font-medium pt-1">{gpsMessage}</p>
          )}
        </div>

        <form onSubmit={handleManualLocationUpdate} className="lg:col-span-6 flex flex-wrap items-center justify-end gap-2">
          <input
            type="text"
            value={manualCity}
            onChange={(e) => setManualCity(e.target.value)}
            placeholder="City label..."
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white w-36"
          />
          <input
            type="text"
            value={manualLat}
            onChange={(e) => setManualLat(e.target.value)}
            placeholder="Latitude"
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white w-24 font-mono"
          />
          <input
            type="text"
            value={manualLon}
            onChange={(e) => setManualLon(e.target.value)}
            placeholder="Longitude"
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white w-24 font-mono"
          />
          <button
            type="submit"
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
          >
            Set Manual Coordinates
          </button>
        </form>
      </div>

      {/* Key Demonstration Scenario: Cross-Module Gym Membership */}
      {gymScenario && (
        <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/30 border border-cyan-500/30 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  Cross-Module Intelligence Demo
                </span>
                <span className="text-xs text-slate-400">
                  Financial Ledger + Subscription Telemetry + Permitted GPS
                </span>
              </div>
              <h2 className="text-lg font-bold text-white mt-1">{gymScenario.scenario_title}</h2>
            </div>

            <div className="text-right">
              <span className="text-xs text-slate-400 block">Potential Savings</span>
              <span className="text-xl font-extrabold text-emerald-400">
                ${gymScenario.savings_calculation.monthly_difference.toFixed(2)}/mo ($
                {gymScenario.savings_calculation.annual_difference.toFixed(0)}/yr)
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1.5">
              <div className="text-slate-400 font-semibold">Current Commitment</div>
              <div className="text-base font-bold text-white">{gymScenario.current_membership.name}</div>
              <div className="text-rose-400 font-bold">${gymScenario.current_membership.monthly_cost.toFixed(2)}/month</div>
              <p className="text-slate-400 text-[11px]">
                • {gymScenario.current_membership.consecutive_monthly_payments} consecutive monthly payments ($270 total)
                <br />• {gymScenario.current_membership.detected_visits_last_45_days} detected visits in last 45 days
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/70 border border-emerald-500/30 space-y-1.5">
              <div className="text-emerald-400 font-semibold">Discovered Local Alternative</div>
              <div className="text-base font-bold text-white">{gymScenario.nearby_alternative.name}</div>
              <div className="text-emerald-400 font-bold">${gymScenario.nearby_alternative.monthly_cost.toFixed(2)}/month</div>
              <p className="text-slate-400 text-[11px]">
                • Distance: {gymScenario.nearby_alternative.distance_miles !== null ? `${gymScenario.nearby_alternative.distance_miles} miles away` : 'Grant GPS or manual location to verify distance'}
                <br />• Net after transport: +${gymScenario.savings_calculation.net_monthly_savings_after_transport}/mo
                <br />• Provenance: {gymScenario.nearby_alternative.price_verification}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/70 border border-amber-500/30 space-y-1.5">
              <div className="text-amber-300 font-semibold flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4" />
                Evidence & Uncertainty Disclosure
              </div>
              <p className="text-[11px] text-slate-300 leading-relaxed">
                <strong>Status:</strong> {gymScenario.evidence_and_caveats.classification}
                <br />• {gymScenario.evidence_and_caveats.missing_records_disclosure}
                <br />• {gymScenario.evidence_and_caveats.alternative_branches_caveat}
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="text-xs font-bold text-cyan-300">FINORA AI Advisor Conclusion:</div>
              <p className="text-sm font-medium text-white italic">"{gymScenario.advisor_message}"</p>
              <p className="text-[11px] text-slate-400">{gymScenario.user_permission_policy}</p>
            </div>

            <button
              onClick={() => handleCheckoutSwitch('sav_gym_planet_20', 'Planet Fitness Classic Membership (1st Month Switch)', 20.0)}
              className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs whitespace-nowrap flex items-center gap-2 shadow-lg shadow-emerald-500/20"
            >
              Approve $20/mo Switch in PayPal Sandbox
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Category Selector & Live OpenStreetMap Trigger */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-2">
          {[
            { id: 'fitness', label: 'Gyms & Fitness', icon: Dumbbell },
            { id: 'groceries', label: 'Groceries & Supermarkets', icon: ShoppingCart },
            { id: 'fuel', label: 'Fuel Stations', icon: Fuel },
            { id: 'software', label: 'Cloud & Software', icon: Cpu }
          ].map((cat) => {
            const Icon = cat.icon;
            const active = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  active
                    ? 'bg-cyan-500 text-slate-950 font-bold shadow-md'
                    : 'bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {cat.label}
              </button>
            );
          })}
        </div>

        <button
          onClick={handleQueryLiveOsm}
          disabled={loadingOsm}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-cyan-500/30 text-xs font-semibold"
        >
          <Globe className="w-3.5 h-3.5" />
          {loadingOsm ? 'Querying OpenStreetMap...' : 'Query Live OpenStreetMap Places Near Coordinates'}
        </button>
      </div>

      {/* Transport-Adjusted Price Comparison Cards */}
      {alternatives.length === 0 ? (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-rose-500/30 text-center space-y-2">
          <div className="text-sm font-bold text-rose-300">
            Location Discovery Paused (Permission Revoked or Denied)
          </div>
          <p className="text-xs text-slate-400 max-w-xl mx-auto">
            FINORA respects your privacy and never silently falls back to default coordinates when location permission is revoked.
            Grant one-time Browser GPS or set manual coordinates above to discover nearby alternatives.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {alternatives.map((alt) => {
            const sav = alt.savings_analysis;
            return (
              <div
                key={alt.candidate_id}
                className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between space-y-4"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-bold text-white text-base">{alt.business_name}</h3>
                      <p className="text-xs text-slate-400">{alt.address} • {alt.distance_miles} miles away</p>
                    </div>
                    <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-cyan-300 text-[10px] font-semibold border border-slate-700">
                      {alt.price_status}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {(alt.facilities || []).map((f: string, idx: number) => (
                      <span key={idx} className="px-2 py-0.5 rounded bg-slate-950 text-slate-300 text-[11px] border border-slate-800">
                        {f}
                      </span>
                    ))}
                  </div>
                </div>

                {sav && (
                  <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800/90 grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="text-slate-500 block text-[10px]">Monthly Price</span>
                      <span className="text-white font-bold text-sm">${alt.monthly_price.toFixed(2)}/mo</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Est. Transport Cost</span>
                      <span className="text-amber-400 font-semibold text-sm">
                        ${sav.estimated_monthly_transport_cost.toFixed(2)}/mo
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Net Monthly Savings</span>
                      <span className={`font-bold text-sm ${sav.is_financially_beneficial ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {sav.net_monthly_savings >= 0 ? '+' : ''}${sav.net_monthly_savings.toFixed(2)}/mo
                      </span>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/80">
                  <span>Hours: {alt.opening_hours}</span>
                  <span>Source: {alt.verification_source}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Live OpenStreetMap Discovery Results */}
      {liveOsmResult && (
        <div className="p-5 rounded-2xl bg-slate-900/90 border border-cyan-500/30 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Globe className="w-4 h-4 text-cyan-400" />
              Live OpenStreetMap Overpass Discovery ({liveOsmResult.status})
            </h3>
            <span className="text-[11px] text-slate-400">
              Never fabricates store prices — live listings show verified coordinates & hours
            </span>
          </div>

          {liveOsmResult.reason && (
            <p className="text-xs text-amber-300">{liveOsmResult.reason}</p>
          )}

          {liveOsmResult.places && liveOsmResult.places.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {liveOsmResult.places.map((p: any) => (
                <div key={p.place_id} className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1">
                  <div className="font-bold text-white">{p.business_name}</div>
                  <div className="text-cyan-400 font-mono text-[11px]">{p.distance_miles} miles away</div>
                  <div className="text-slate-400 text-[11px]">{p.address}</div>
                  <div className="text-[10px] text-amber-300 pt-1">{p.price_status}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

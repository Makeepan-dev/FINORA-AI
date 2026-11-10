import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  ShoppingBag,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Star,
  Truck,
  ShieldCheck,
  Scale,
  Sparkles,
  Loader2
} from 'lucide-react';
import { api } from '../services/api';
import { ProductItem, BudgetEvaluation } from '../types';

interface ShoppingProps {
  onSelectForCheckout: (product: ProductItem) => void;
  activeUserId: string;
}

const CATEGORIES = [
  { id: 'all', label: 'All Products' },
  { id: 'electronics', label: 'Electronics & Displays' },
  { id: 'audio', label: 'Audio & Acoustics' },
  { id: 'office', label: 'Ergonomic Office' },
  { id: 'fitness', label: 'Fitness & Recovery' },
  { id: 'home', label: 'Smart Home & Lighting' },
  { id: 'software', label: 'Developer Software' },
];

export const Shopping: React.FC<ShoppingProps> = ({ onSelectForCheckout, activeUserId }) => {
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEvaluation, setSelectedEvaluation] = useState<BudgetEvaluation | null>(null);
  const [evaluatingProductId, setEvaluatingProductId] = useState<string | null>(null);

  // Comparison State
  const [comparisonItems, setComparisonItems] = useState<ProductItem[]>([]);
  const [showComparisonModal, setShowComparisonModal] = useState(false);

  useEffect(() => {
    loadProducts();
  }, [selectedCategory]);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const prods = await api.searchProducts(searchQuery, selectedCategory);
      setProducts(prods);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadProducts();
  };

  const handleEvaluateBudget = async (prod: ProductItem) => {
    setEvaluatingProductId(prod.product_id);
    try {
      const evaluation = await api.evaluateBudget(prod.product_id, activeUserId);
      setSelectedEvaluation(evaluation);
    } catch (err) {
      console.error(err);
    } finally {
      setEvaluatingProductId(null);
    }
  };

  const toggleCompare = (prod: ProductItem) => {
    if (comparisonItems.some(p => p.product_id === prod.product_id)) {
      setComparisonItems(prev => prev.filter(p => p.product_id !== prod.product_id));
    } else {
      if (comparisonItems.length >= 3) {
        alert("You can compare up to 3 products at a time.");
        return;
      }
      setComparisonItems(prev => [...prev, prod]);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Autonomous Shopping Agent</h1>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Fictional Catalogue (105 Items)
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Budget-aware product discovery, total landed cost calculations, and seamless PayPal checkout
          </p>
        </div>

        {comparisonItems.length > 0 && (
          <button
            onClick={() => setShowComparisonModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20 hover:bg-cyan-400 transition-all"
          >
            <Scale className="w-4 h-4" />
            <span>Compare Selected ({comparisonItems.length})</span>
          </button>
        )}
      </div>

      {/* Category Tabs & Search Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-1.5">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                selectedCategory === cat.id
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search monitor, keyboard, desk..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-72"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold border border-slate-700"
          >
            Filter
          </button>
        </form>
      </div>

      {/* Products Grid */}
      {loading ? (
        <div className="flex items-center justify-center p-20 text-slate-400 text-sm gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-cyan-400" />
          <span>Searching product catalogue...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {products.map((prod) => {
            const isComparing = comparisonItems.some(p => p.product_id === prod.product_id);
            return (
              <div
                key={prod.product_id}
                className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/80 hover:border-slate-700 transition-all space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-2.5">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                      {prod.category}
                    </span>
                    <button
                      onClick={() => toggleCompare(prod)}
                      className={`text-[11px] font-semibold flex items-center gap-1 px-2 py-0.5 rounded transition-all ${
                        isComparing
                          ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <Scale className="w-3 h-3" />
                      <span>{isComparing ? 'Comparing' : 'Compare'}</span>
                    </button>
                  </div>

                  <h3 className="font-bold text-white text-base leading-snug">{prod.product_name}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{prod.description}</p>

                  {/* Pricing Breakdown */}
                  <div className="pt-2 flex items-baseline justify-between border-t border-slate-800/60">
                    <div>
                      <span className="text-xl font-black text-white">${prod.price.toFixed(2)}</span>
                      {prod.shipping_cost > 0 ? (
                        <span className="text-[11px] text-slate-400 ml-1.5">+${prod.shipping_cost.toFixed(2)} shipping</span>
                      ) : (
                        <span className="text-[11px] text-emerald-400 font-semibold ml-1.5">Free Shipping</span>
                      )}
                    </div>
                    <span className="text-xs text-slate-400 font-medium">Total: ${prod.total_cost.toFixed(2)}</span>
                  </div>

                  {/* Highlights (delivery, warranty, rating) */}
                  <div className="grid grid-cols-3 gap-2 py-2 text-[10px] text-slate-400 border-t border-slate-800/60">
                    <div className="flex items-center gap-1">
                      <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                      <span>{prod.rating} ({prod.review_count})</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Truck className="w-3 h-3 text-cyan-400" />
                      <span>{prod.delivery_days}d delivery</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <ShieldCheck className="w-3 h-3 text-emerald-400" />
                      <span>{prod.warranty_months}mo warranty</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800">
                  <button
                    onClick={() => handleEvaluateBudget(prod)}
                    disabled={evaluatingProductId === prod.product_id}
                    className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition-colors flex items-center justify-center gap-1.5"
                  >
                    {evaluatingProductId === prod.product_id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                    ) : (
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                    )}
                    <span>Check Budget</span>
                  </button>

                  <button
                    onClick={() => onSelectForCheckout(prod)}
                    className="w-full py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-all shadow-md shadow-cyan-500/20 flex items-center justify-center gap-1"
                  >
                    <ShoppingBag className="w-3.5 h-3.5" />
                    <span>PayPal Checkout</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Budget Evaluation Drawer / Modal */}
      {selectedEvaluation && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg rounded-2xl bg-slate-900 border border-slate-700 p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-white text-base">Budget Impact Analysis</h3>
              </div>
              <button
                onClick={() => setSelectedEvaluation(null)}
                className="text-slate-400 hover:text-white text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-400 block">Item Name:</span>
                <span className="font-bold text-white text-sm">{selectedEvaluation.product_name}</span>
              </div>

              <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <div>
                  <span className="text-slate-400 block text-[11px]">Base Product Price:</span>
                  <span className="font-semibold text-white">${selectedEvaluation.price.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Shipping Cost:</span>
                  <span className="font-semibold text-white">${selectedEvaluation.shipping_cost.toFixed(2)}</span>
                </div>
                <div className="col-span-2 pt-1 border-t border-slate-700 flex justify-between items-baseline">
                  <span className="font-bold text-slate-300">Total Landed Cost:</span>
                  <span className="font-extrabold text-white text-base">${selectedEvaluation.total_cost.toFixed(2)}</span>
                </div>
              </div>

              <div className="space-y-1.5 pt-2">
                <div className="flex justify-between">
                  <span className="text-slate-400">Monthly Category Budget:</span>
                  <span className="text-slate-200 font-semibold">${selectedEvaluation.monthly_category_limit.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Remaining Budget (Before):</span>
                  <span className="text-slate-200 font-semibold">${selectedEvaluation.remaining_budget_before_purchase.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Remaining Budget (After Purchase):</span>
                  <span className={`font-bold ${selectedEvaluation.is_within_budget ? 'text-emerald-400' : 'text-rose-400'}`}>
                    ${selectedEvaluation.remaining_budget_after_purchase.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Status Alert */}
              <div className={`p-4 rounded-xl flex items-start gap-3 border ${
                selectedEvaluation.is_within_budget
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              }`}>
                {selectedEvaluation.is_within_budget ? (
                  <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5 text-emerald-400" />
                ) : (
                  <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-400" />
                )}
                <div>
                  <span className="font-bold block text-sm">
                    {selectedEvaluation.is_within_budget ? "Within Budget" : "Exceeds Budget Threshold"}
                  </span>
                  <p className="text-[11px] text-slate-300 mt-1 leading-relaxed">
                    {selectedEvaluation.recommendation}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => setSelectedEvaluation(null)}
                className="w-1/2 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const prod = products.find(p => p.product_id === selectedEvaluation.product_id);
                  setSelectedEvaluation(null);
                  if (prod) onSelectForCheckout(prod);
                }}
                className="w-1/2 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Modal */}
      {showComparisonModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-3xl rounded-2xl bg-slate-900 border border-slate-700 p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <Scale className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-white text-base">Product Comparison ({comparisonItems.length})</h3>
              </div>
              <button
                onClick={() => setShowComparisonModal(false)}
                className="text-slate-400 hover:text-white text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {comparisonItems.map((item) => (
                <div key={item.product_id} className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-3">
                  <h4 className="font-bold text-white text-sm leading-snug">{item.product_name}</h4>
                  <div className="text-xl font-black text-cyan-400">
                    ${item.total_cost.toFixed(2)}
                  </div>
                  <div className="text-xs space-y-1.5 text-slate-300 pt-2 border-t border-slate-700">
                    <div>Price: <span className="text-white">${item.price.toFixed(2)}</span></div>
                    <div>Shipping: <span className="text-white">${item.shipping_cost.toFixed(2)}</span></div>
                    <div>Delivery: <span className="text-white">{item.delivery_days} days</span></div>
                    <div>Warranty: <span className="text-white">{item.warranty_months} months</span></div>
                  </div>
                  <button
                    onClick={() => {
                      setShowComparisonModal(false);
                      onSelectForCheckout(item);
                    }}
                    className="w-full py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-colors"
                  >
                    Select this item
                  </button>
                </div>
              ))}
            </div>

            <button
              onClick={() => setShowComparisonModal(false)}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
            >
              Close Comparison
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

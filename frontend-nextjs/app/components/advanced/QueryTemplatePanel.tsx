"use client";

import React, { useState } from "react";
import { Plus, Trash2, Copy, TrendingUp } from "lucide-react";
import { useQueryTemplates } from "@/app/hooks/useQueryTemplates";

export function QueryTemplatePanel() {
  const { templates, addTemplate, deleteTemplate, useTemplate, getTemplatesByCategory } =
    useQueryTemplates();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    query: "",
    category: "general",
    description: "",
  });

  const handleAddTemplate = () => {
    if (formData.name && formData.query) {
      addTemplate({
        ...formData,
        parameters: [],
      });
      setFormData({ name: "", query: "", category: "general", description: "" });
      setShowForm(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Add Template Button */}
      <button
        onClick={() => setShowForm(!showForm)}
        className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        <Plus className="w-4 h-4" />
        New Template
      </button>

      {/* Add Template Form */}
      {showForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
          <input
            type="text"
            placeholder="Template name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
          />
          <textarea
            placeholder="Query text"
            value={formData.query}
            onChange={(e) => setFormData({ ...formData, query: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
            rows={3}
          />
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
          >
            <option value="general">General</option>
            <option value="vendor">Vendor</option>
            <option value="compliance">Compliance</option>
            <option value="audit">Audit</option>
          </select>
          <input
            type="text"
            placeholder="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
          />
          <button
            onClick={handleAddTemplate}
            className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
          >
            Save Template
          </button>
        </div>
      )}

      {/* Templates Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {templates.map((template) => (
          <div key={template.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{template.name}</h4>
                <p className="text-xs text-gray-500">{template.category}</p>
              </div>
              <span className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                <TrendingUp className="w-3 h-3" />
                {template.usageCount}
              </span>
            </div>

            <p className="text-sm text-gray-600 mb-3">{template.description}</p>
            <p className="text-xs text-gray-500 mb-3 line-clamp-2">"{template.query}"</p>

            <div className="flex gap-2">
              <button
                onClick={() => useTemplate(template.id)}
                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                <Copy className="w-4 h-4" />
                Use
              </button>
              <button
                onClick={() => deleteTemplate(template.id)}
                className="px-3 py-2 bg-red-100 text-red-600 rounded hover:bg-red-200"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

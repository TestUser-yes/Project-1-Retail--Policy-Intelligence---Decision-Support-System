'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  MessageSquare,
  Book,
  Database,
  FileText,
  AlertTriangle,
  Activity,
  BarChart3,
  CheckSquare,
  Settings,
  Shield,
  ChevronDown,
  Menu,
  X,
} from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  description?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const NAVIGATION: NavSection[] = [
  {
    title: 'Platform',
    items: [
      {
        label: 'Dashboard',
        href: '/dashboard',
        icon: LayoutDashboard,
        description: 'System overview and KPIs',
      },
      {
        label: 'Query Assistant',
        href: '/query',
        icon: MessageSquare,
        description: 'Ask compliance questions',
      },
    ],
  },
  {
    title: 'Knowledge & Compliance',
    items: [
      {
        label: 'Policy Explorer',
        href: '/policy-explorer',
        icon: Book,
        description: 'Browse all policies',
      },
      {
        label: 'Compliance Database',
        href: '/compliance',
        icon: Database,
        description: 'Vendor and audit records',
      },
      {
        label: 'Audit Logs',
        href: '/audit',
        icon: FileText,
        description: 'System audit trail',
      },
    ],
  },
  {
    title: 'Operations',
    items: [
      {
        label: 'Escalation Center',
        href: '/escalation-center',
        icon: AlertTriangle,
        description: 'High-risk case management',
      },
      {
        label: 'Observability',
        href: '/observability',
        icon: Activity,
        description: 'System metrics & traces',
      },
      {
        label: 'Evaluation',
        href: '/evaluation',
        icon: CheckSquare,
        description: 'SLO and quality metrics',
      },
    ],
  },
  {
    title: 'Administration',
    items: [
      {
        label: 'Admin Panel',
        href: '/admin',
        icon: BarChart3,
        description: 'System configuration',
      },
      {
        label: 'Settings',
        href: '/admin/settings',
        icon: Settings,
        description: 'User and system settings',
      },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [expandedSection, setExpandedSection] = useState<string | null>('Platform');

  const isActive = (href: string) => pathname === href;

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const NavContent = () => (
    <div className="space-y-1">
      {NAVIGATION.map((section) => (
        <div key={section.title} className="mb-6">
          <button
            onClick={() => toggleSection(section.title)}
            className="w-full flex items-center justify-between px-4 py-2 text-xs font-bold text-gray-600 uppercase tracking-wider hover:text-gray-900 transition"
          >
            <span>{section.title}</span>
            <ChevronDown
              className={`w-4 h-4 transition transform ${
                expandedSection === section.title ? 'rotate-180' : ''
              }`}
            />
          </button>

          {expandedSection === section.title && (
            <div className="mt-2 space-y-1">
              {section.items.map((item) => {
                const active = isActive(item.href);
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setIsOpen(false)}
                    className={`group flex items-start gap-3 px-4 py-3 rounded-lg transition ${
                      active
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'text-gray-700 hover:bg-gray-100 hover:text-blue-600'
                    }`}
                  >
                    <Icon
                      className={`w-5 h-5 mt-0.5 flex-shrink-0 transition ${
                        active ? 'text-white' : 'text-gray-500 group-hover:text-blue-600'
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-semibold ${active ? 'text-white' : 'text-gray-900'}`}>
                        {item.label}
                      </p>
                      <p
                        className={`text-xs ${
                          active ? 'text-blue-100' : 'text-gray-600'
                        }`}
                      >
                        {item.description}
                      </p>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <>
      {/* Mobile Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed bottom-6 right-6 z-40 p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700"
      >
        {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Desktop Sidebar */}
      <div className="hidden md:flex flex-col fixed left-0 top-0 h-screen w-64 bg-white border-r-2 border-slate-200 shadow-sm z-30 overflow-y-auto">
        {/* Logo Section */}
        <div className="flex items-center gap-3 px-6 py-6 border-b-2 border-slate-200">
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="font-bold text-gray-900">Policy</p>
            <p className="text-xs text-gray-600">Intelligence</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-6 overflow-y-auto">
          <NavContent />
        </nav>

        {/* Footer */}
        <div className="border-t-2 border-slate-200 p-6 bg-slate-50">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs font-bold text-blue-900 uppercase mb-2">SLO Status</p>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs text-blue-800">Success Rate</span>
                <span className="text-xs font-bold text-green-600">94%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-blue-800">Latency</span>
                <span className="text-xs font-bold text-green-600">2.1s</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Sidebar */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 z-20 bg-black/50">
          <div className="absolute left-0 top-0 h-full w-64 bg-white shadow-lg overflow-y-auto">
            {/* Logo */}
            <div className="flex items-center gap-3 px-6 py-6 border-b-2 border-slate-200">
              <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="font-bold text-gray-900">Policy</p>
                <p className="text-xs text-gray-600">Intelligence</p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="px-3 py-6">
              <NavContent />
            </nav>
          </div>
        </div>
      )}

      {/* Main Content Offset for Desktop */}
      <div className="hidden md:block fixed left-0 top-0 w-64 h-screen pointer-events-none" />
    </>
  );
}

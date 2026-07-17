import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download } from 'lucide-react'; // Import icon
import { exportToCSV } from '../utils/csvExporter'; // Import your CSV utility

interface LeadTableProps {
  leads: any[]; 
  isLoading: boolean;
}

const LeadTable: React.FC<LeadTableProps> = ({ leads, isLoading }) => {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const handleExport = () => {
    if (leads.length > 0) {
      // Assuming your csvExporter takes the data and a filename
      exportToCSV(leads, 'omnicrew_extracted_entities.csv');
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Export Button Header */}
      <div className="flex justify-end mb-2">
        <button 
          onClick={handleExport} 
          disabled={leads.length === 0 || isLoading}
          className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-primary transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <Download size={14} />
          Export CSV
        </button>
      </div>

      <div style={{ maxHeight: '350px', overflowY: 'auto', width: '100%' }}>
        {isLoading ? (
          <div style={{ padding: '1rem', textAlign: 'center', color: '#86868b' }}>Scanning data streams...</div>
        ) : leads.length === 0 ? (
          <div style={{ padding: '1rem', textAlign: 'center', color: '#86868b' }}>No entities extracted yet.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', color: '#e0e0e0' }}>
            <thead style={{ position: 'sticky', top: 0, backgroundColor: '#0a0a0a', zIndex: 10 }}>
              <tr style={{ borderBottom: '1px solid #333', textAlign: 'left' }}>
                <th style={{ padding: '10px', width: '30px' }}></th>
                <th style={{ padding: '10px' }}>Entity Name</th>
                <th style={{ padding: '10px' }}>Classification</th>
                <th style={{ padding: '10px' }}>Source URL</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => {
                const isExpanded = expandedId === lead.id;
                return (
                  <React.Fragment key={lead.id}>
                    {/* Main Row with Data-Flash Animation */}
                    <motion.tr
                      initial={{ backgroundColor: 'rgba(0, 255, 136, 0.2)' }} 
                      animate={{ backgroundColor: 'rgba(0, 255, 136, 0)' }}    
                      transition={{ duration: 1.5, ease: 'easeOut' }}
                      onClick={() => toggleExpand(lead.id)}
                      style={{ cursor: 'pointer', borderBottom: '1px solid #222' }}
                    >
                      <td style={{ padding: '12px 10px', color: '#ff9f43', fontWeight: 'bold' }}>
                        <motion.span animate={{ rotate: isExpanded ? 90 : 0 }} transition={{ duration: 0.2 }}>
                          ›
                        </motion.span>
                      </td>
                      <td style={{ padding: '12px 10px', fontWeight: 500 }}>{lead.entity_name}</td>
                      <td style={{ padding: '12px 10px', color: '#86868b' }}>{lead.classification}</td>
                      <td style={{ padding: '12px 10px', color: '#86868b', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        <a href={lead.source_url} target="_blank" rel="noreferrer" style={{ color: '#61dafb', textDecoration: 'none' }}>
                          {lead.source_url.replace('https://', '').replace('http://', '').split('/')[0]}
                        </a>
                      </td>
                    </motion.tr>
                    
                    {/* Expandable JSON Payload Row */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.tr
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.3, ease: 'easeInOut' }}
                        >
                          <td colSpan={4} style={{ padding: 0, border: 'none' }}>
                            <motion.div
                              initial={{ y: -10 }}
                              animate={{ y: 0 }}
                              style={{
                                background: 'rgba(0, 0, 0, 0.3)',
                                padding: '15px',
                                margin: '5px 10px',
                                borderRadius: '4px',
                                border: '1px solid #333',
                                overflowX: 'auto'
                              }}
                            >
                              <pre style={{ margin: 0, color: '#a9b7c6', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                                {JSON.stringify(lead.data_payload, null, 2)}
                              </pre>
                            </motion.div>
                          </td>
                        </motion.tr>
                      )}
                    </AnimatePresence>
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default LeadTable;
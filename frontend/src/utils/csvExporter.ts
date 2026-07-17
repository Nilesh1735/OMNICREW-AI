import { LeadData } from '../types';

// Added filename parameter to match the call in LeadTable.tsx
export const exportToCSV = (leads: LeadData[], filename: string = `omnicrew_extraction_${Date.now()}.csv`) => {
  if (!leads || leads.length === 0) {
    alert('No data available to export.');
    return;
  }

  // 1. Extract all unique keys from data_payload across all leads
  const dynamicKeys = new Set<string>();
  leads.forEach(lead => {
    if (lead.data_payload) {
      Object.keys(lead.data_payload).forEach(key => dynamicKeys.add(key));
    }
  });

  const dynamicHeaders = Array.from(dynamicKeys);
  const staticHeaders = ['Entity Name', 'Classification', 'Source URL', 'Extracted At'];
  const headers = [...dynamicHeaders, ...staticHeaders];

  // 2. Map leads to rows
  const rows = leads.map(lead => {
    const row: (string | number)[] = [];
    
    // Add dynamic payload values
    dynamicHeaders.forEach(header => {
      const val = lead.data_payload?.[header] ?? 'N/A';
      row.push(escapeCSVValue(val));
    });

    // Add static values
    row.push(escapeCSVValue(lead.entity_name));
    row.push(escapeCSVValue(lead.classification));
    row.push(escapeCSVValue(lead.source_url));
    row.push(escapeCSVValue(new Date(lead.extracted_at).toLocaleString()));
    
    return row.join(',');
  });

  // 3. Combine and trigger download using the provided filename
  const csvContent = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename); // Use the passed filename here
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Helper to escape commas, quotes, and newlines for CSV format
const escapeCSVValue = (value: any): string => {
  const strValue = String(value);
  if (strValue.includes(',') || strValue.includes('"') || strValue.includes('\n')) {
    return `"${strValue.replace(/"/g, '""')}"`;
  }
  return strValue;
};
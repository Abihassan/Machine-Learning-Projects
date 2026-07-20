import { AnalysisResult } from './types';

export const analyzeUrl = async (url: string): Promise<AnalysisResult> => {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 2000));

  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    throw new Error("Invalid URL format. Must start with http:// or https://");
  }

  // Simulate randomized ML analysis based on simple URL parsing
  const isHttp = url.startsWith('http://');
  const hasIp = /\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/.test(url);
  const length = url.length;
  
  // Calculate a mock score (lower is more dangerous)
  let score = 100;
  if (isHttp) score -= 30;
  if (hasIp) score -= 40;
  if (length > 75) score -= 15;
  if (url.includes('@')) score -= 25;

  score = Math.max(0, Math.min(100, score)); // Clamp between 0-100

  let verdict: 'Safe' | 'Suspicious' | 'Malicious' = 'Safe';
  if (score < 40) verdict = 'Malicious';
  else if (score < 75) verdict = 'Suspicious';

  return {
    url,
    trustScore: score,
    verdict,
    structure: {
      isLong: length > 75,
      hasAtSymbol: url.includes('@'),
      hasMultipleHyphens: (url.match(/-/g) || []).length > 3,
      isIpAddress: hasIp,
      subdomainCount: Math.floor(Math.random() * 4),
      suspiciousTld: url.endsWith('.xyz') || url.endsWith('.top'),
    },
    security: {
      hasHttps: !isHttp,
      validSsl: !isHttp && score > 30,
      domainAgeDays: Math.floor(Math.random() * 3000),
      hasRedirects: Math.random() > 0.7,
    }
  };
};
export interface AnalysisResult {
  url: string;
  trustScore: number;
  verdict: 'Safe' | 'Suspicious' | 'Malicious';
  structure: {
    isLong: boolean;
    hasAtSymbol: boolean;
    hasMultipleHyphens: boolean;
    isIpAddress: boolean;
    subdomainCount: number;
    suspiciousTld: boolean;
  };
  security: {
    hasHttps: boolean;
    validSsl: boolean;
    domainAgeDays: number;
    hasRedirects: boolean;
  };
}
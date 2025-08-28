"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const opal_tools_sdk_1 = require("@optimizely-opal/opal-tools-sdk");
const axios_1 = __importDefault(require("axios"));
const cheerio = __importStar(require("cheerio"));
// Create Express app
const app = (0, express_1.default)();
app.use(express_1.default.json());
// Create Tools Service
const toolsService = new opal_tools_sdk_1.ToolsService(app);
/**
 * Greeting Tool: Greets a person in a random language
 */
// Apply tool decorator after function definition
async function greeting(parameters) {
    const { name, language } = parameters;
    // If language not specified, choose randomly
    const selectedLanguage = language ||
        ['english', 'spanish', 'french'][Math.floor(Math.random() * 3)];
    // Generate greeting based on language
    let greeting;
    if (selectedLanguage.toLowerCase() === 'spanish') {
        greeting = `¡Hola, ${name}! ¿Cómo estás?`;
    }
    else if (selectedLanguage.toLowerCase() === 'french') {
        greeting = `Bonjour, ${name}! Comment ça va?`;
    }
    else { // Default to English
        greeting = `Hello, ${name}! How are you?`;
    }
    return {
        greeting,
        language: selectedLanguage
    };
}
/**
 * Today's Date Tool: Returns today's date in the specified format
 */
// Apply tool decorator after function definition
async function todaysDate(parameters) {
    const format = parameters.format || '%Y-%m-%d';
    // Get today's date
    const today = new Date();
    // Format the date (simplified implementation)
    let formattedDate;
    if (format === '%Y-%m-%d') {
        formattedDate = today.toISOString().split('T')[0];
    }
    else if (format === '%B %d, %Y') {
        formattedDate = today.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
    else if (format === '%d/%m/%Y') {
        formattedDate = today.toLocaleDateString('en-GB');
    }
    else {
        // Default to ISO format
        formattedDate = today.toISOString().split('T')[0];
    }
    return {
        date: formattedDate,
        format: format,
        timestamp: today.getTime() / 1000
    };
}
/**
 * SEO Tool: Fetches SEO meta tags from a URL
 */
async function fetchSeoInfo(parameters) {
    const { url } = parameters;
    try {
        // Fetch the HTML content
        const response = await axios_1.default.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (compatible; OpalSEOBot/1.0)',
            },
            timeout: 10000,
        });
        // Load HTML into cheerio
        const $ = cheerio.load(response.data);
        // Extract SEO information
        const seoInfo = {
            // Basic tags
            title: $('title').text() || null,
            metaDescription: $('meta[name="description"]').attr('content') || null,
            metaKeywords: $('meta[name="keywords"]').attr('content') || null,
            canonical: $('link[rel="canonical"]').attr('href') || null,
            robots: $('meta[name="robots"]').attr('content') || null,
            // Open Graph tags
            ogTitle: $('meta[property="og:title"]').attr('content') || null,
            ogDescription: $('meta[property="og:description"]').attr('content') || null,
            ogImage: $('meta[property="og:image"]').attr('content') || null,
            ogUrl: $('meta[property="og:url"]').attr('content') || null,
            ogType: $('meta[property="og:type"]').attr('content') || null,
            ogSiteName: $('meta[property="og:site_name"]').attr('content') || null,
            // Twitter Card tags
            twitterCard: $('meta[name="twitter:card"]').attr('content') || null,
            twitterTitle: $('meta[name="twitter:title"]').attr('content') || null,
            twitterDescription: $('meta[name="twitter:description"]').attr('content') || null,
            twitterImage: $('meta[name="twitter:image"]').attr('content') || null,
            twitterSite: $('meta[name="twitter:site"]').attr('content') || null,
            twitterCreator: $('meta[name="twitter:creator"]').attr('content') || null,
            // Additional SEO relevant tags
            viewport: $('meta[name="viewport"]').attr('content') || null,
            author: $('meta[name="author"]').attr('content') || null,
            language: $('html').attr('lang') || null,
            charset: $('meta[charset]').attr('charset') || $('meta[http-equiv="Content-Type"]').attr('content') || null,
            // Structured data (JSON-LD)
            jsonLd: [],
        };
        // Extract JSON-LD structured data
        $('script[type="application/ld+json"]').each((_, element) => {
            try {
                const jsonData = JSON.parse($(element).html() || '{}');
                seoInfo.jsonLd.push(jsonData);
            }
            catch (e) {
                // Ignore invalid JSON
            }
        });
        // Count headings for SEO analysis
        const headingCounts = {
            h1: $('h1').length,
            h2: $('h2').length,
            h3: $('h3').length,
            h4: $('h4').length,
            h5: $('h5').length,
            h6: $('h6').length,
        };
        return {
            url,
            success: true,
            seoInfo,
            headingCounts,
            fetchedAt: new Date().toISOString(),
        };
    }
    catch (error) {
        return {
            url,
            success: false,
            error: error.message || 'Failed to fetch SEO information',
            fetchedAt: new Date().toISOString(),
        };
    }
}
// Register the tools using decorators with explicit parameter definitions
(0, opal_tools_sdk_1.tool)({
    name: 'greeting',
    description: 'Greets a person in a random language (English, Spanish, or French)',
    parameters: [
        {
            name: 'name',
            type: opal_tools_sdk_1.ParameterType.String,
            description: 'Name of the person to greet',
            required: true
        },
        {
            name: 'language',
            type: opal_tools_sdk_1.ParameterType.String,
            description: 'Language for greeting (defaults to random)',
            required: false
        }
    ]
})(greeting);
(0, opal_tools_sdk_1.tool)({
    name: 'todays-date',
    description: 'Returns today\'s date in the specified format',
    parameters: [
        {
            name: 'format',
            type: opal_tools_sdk_1.ParameterType.String,
            description: 'Date format (defaults to ISO format)',
            required: false
        }
    ]
})(todaysDate);
(0, opal_tools_sdk_1.tool)({
    name: 'fetch-seo-info',
    description: 'Fetches SEO meta tags and information from a specified URL',
    parameters: [
        {
            name: 'url',
            type: opal_tools_sdk_1.ParameterType.String,
            description: 'The URL to fetch SEO information from',
            required: true
        }
    ]
})(fetchSeoInfo);
/**
 * GEO Analysis Tool: Analyzes if a URL is optimized for LLMs (ChatGPT, Claude, etc.)
 */
async function analyzeGeoOptimization(parameters) {
    const { url } = parameters;
    try {
        // Fetch the HTML content
        const response = await axios_1.default.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (compatible; OpalGEOBot/1.0)',
            },
            timeout: 10000,
        });
        // Load HTML into cheerio
        const $ = cheerio.load(response.data);
        // Initialize GEO analysis results
        const geoIndicators = {
            // Structured data presence
            hasJsonLd: false,
            hasSchemaOrg: false,
            structuredDataTypes: [],
            // Content quality indicators
            hasClearHeadings: false,
            hasMetaDescription: false,
            hasSemanticHTML: false,
            // FAQ and Q&A optimization
            hasFAQSchema: false,
            hasHowToSchema: false,
            hasQAPageSchema: false,
            // Content clarity indicators
            hasDefinitions: false,
            hasLists: false,
            hasTables: false,
            hasCodeBlocks: false,
            // Authority signals
            hasAuthorInfo: false,
            hasDateInfo: false,
            hasCitations: false,
            // Technical optimization
            hasOpenGraph: false,
            hasCanonicalUrl: false,
            hasRobotsTxt: true, // Assume true, would need separate check
            // Content depth
            wordCount: 0,
            headingStructure: {
                h1: 0,
                h2: 0,
                h3: 0,
                total: 0
            },
            // Specific LLM optimization
            hasLlmSpecificMeta: false,
            llmMetaTags: []
        };
        // Check for JSON-LD structured data
        const jsonLdScripts = $('script[type="application/ld+json"]');
        geoIndicators.hasJsonLd = jsonLdScripts.length > 0;
        // Analyze structured data types
        jsonLdScripts.each((_, element) => {
            try {
                const jsonData = JSON.parse($(element).html() || '{}');
                if (jsonData['@type']) {
                    const types = Array.isArray(jsonData['@type']) ? jsonData['@type'] : [jsonData['@type']];
                    geoIndicators.structuredDataTypes.push(...types);
                    // Check for specific schemas that help LLMs
                    if (types.includes('FAQPage'))
                        geoIndicators.hasFAQSchema = true;
                    if (types.includes('HowTo'))
                        geoIndicators.hasHowToSchema = true;
                    if (types.includes('QAPage'))
                        geoIndicators.hasQAPageSchema = true;
                }
                // Handle arrays of structured data
                if (Array.isArray(jsonData)) {
                    jsonData.forEach(item => {
                        if (item['@type']) {
                            const types = Array.isArray(item['@type']) ? item['@type'] : [item['@type']];
                            geoIndicators.structuredDataTypes.push(...types);
                            if (types.includes('FAQPage'))
                                geoIndicators.hasFAQSchema = true;
                            if (types.includes('HowTo'))
                                geoIndicators.hasHowToSchema = true;
                            if (types.includes('QAPage'))
                                geoIndicators.hasQAPageSchema = true;
                        }
                    });
                }
            }
            catch (e) {
                // Ignore invalid JSON
            }
        });
        // Check for Schema.org microdata
        geoIndicators.hasSchemaOrg = $('[itemscope][itemtype*="schema.org"]').length > 0;
        // Check heading structure
        const h1Count = $('h1').length;
        const h2Count = $('h2').length;
        const h3Count = $('h3').length;
        geoIndicators.headingStructure = {
            h1: h1Count,
            h2: h2Count,
            h3: h3Count,
            total: h1Count + h2Count + h3Count
        };
        geoIndicators.hasClearHeadings = h1Count >= 1 && h2Count >= 2;
        // Check for meta description
        geoIndicators.hasMetaDescription = !!$('meta[name="description"]').attr('content');
        // Check for semantic HTML5 elements
        const semanticElements = ['article', 'section', 'nav', 'aside', 'header', 'footer', 'main'];
        geoIndicators.hasSemanticHTML = semanticElements.some(elem => $(elem).length > 0);
        // Check for content clarity indicators
        geoIndicators.hasDefinitions = $('dl, dfn').length > 0;
        geoIndicators.hasLists = $('ul, ol').length > 0;
        geoIndicators.hasTables = $('table').length > 0;
        geoIndicators.hasCodeBlocks = $('pre, code').length > 0;
        // Check for author information
        geoIndicators.hasAuthorInfo =
            $('meta[name="author"]').length > 0 ||
                $('[itemprop="author"]').length > 0 ||
                $('.author, .by-author, .post-author').length > 0;
        // Check for date information
        geoIndicators.hasDateInfo =
            $('time').length > 0 ||
                $('[itemprop="datePublished"]').length > 0 ||
                $('[itemprop="dateModified"]').length > 0 ||
                $('meta[property="article:published_time"]').length > 0;
        // Check for citations/references
        geoIndicators.hasCitations =
            $('cite').length > 0 ||
                $('.citation, .reference, .bibliography').length > 0 ||
                $('a[href*="doi.org"]').length > 0;
        // Check for Open Graph
        geoIndicators.hasOpenGraph = $('meta[property^="og:"]').length > 0;
        // Check for canonical URL
        geoIndicators.hasCanonicalUrl = $('link[rel="canonical"]').length > 0;
        // Estimate word count
        const textContent = $('body').text();
        geoIndicators.wordCount = textContent.split(/\s+/).filter(word => word.length > 0).length;
        // Check for LLM-specific meta tags
        const llmMetaPatterns = [
            'meta[name*="llm"]',
            'meta[name*="ai"]',
            'meta[name*="gpt"]',
            'meta[name*="claude"]',
            'meta[name*="generative"]',
            'meta[property*="llm"]',
            'meta[property*="ai"]'
        ];
        llmMetaPatterns.forEach(pattern => {
            $(pattern).each((_, element) => {
                const name = $(element).attr('name') || $(element).attr('property');
                if (name) {
                    geoIndicators.llmMetaTags.push(name);
                    geoIndicators.hasLlmSpecificMeta = true;
                }
            });
        });
        // Calculate GEO score (0-100)
        let geoScore = 0;
        const scoreFactors = {
            hasJsonLd: 10,
            hasSchemaOrg: 5,
            hasFAQSchema: 10,
            hasHowToSchema: 8,
            hasQAPageSchema: 8,
            hasClearHeadings: 8,
            hasMetaDescription: 5,
            hasSemanticHTML: 5,
            hasDefinitions: 3,
            hasLists: 3,
            hasTables: 3,
            hasCodeBlocks: 3,
            hasAuthorInfo: 5,
            hasDateInfo: 5,
            hasCitations: 5,
            hasOpenGraph: 3,
            hasCanonicalUrl: 3,
            hasLlmSpecificMeta: 10,
            hasGoodWordCount: (geoIndicators.wordCount >= 500 && geoIndicators.wordCount <= 5000) ? 6 : 0
        };
        Object.entries(scoreFactors).forEach(([key, value]) => {
            if (key === 'hasGoodWordCount') {
                geoScore += value;
            }
            else if (geoIndicators[key]) {
                geoScore += value;
            }
        });
        // Generate recommendations
        const recommendations = [];
        if (!geoIndicators.hasJsonLd) {
            recommendations.push('Add JSON-LD structured data for better LLM understanding');
        }
        if (!geoIndicators.hasFAQSchema && !geoIndicators.hasQAPageSchema) {
            recommendations.push('Consider adding FAQ or Q&A schema for better question-answer extraction');
        }
        if (!geoIndicators.hasClearHeadings) {
            recommendations.push('Improve heading structure with clear H1 and multiple H2 sections');
        }
        if (!geoIndicators.hasAuthorInfo) {
            recommendations.push('Add author information for credibility signals');
        }
        if (!geoIndicators.hasDateInfo) {
            recommendations.push('Include publication/update dates for content freshness signals');
        }
        if (geoIndicators.wordCount < 300) {
            recommendations.push('Consider adding more comprehensive content (current word count: ' + geoIndicators.wordCount + ')');
        }
        if (!geoIndicators.hasSemanticHTML) {
            recommendations.push('Use semantic HTML5 elements (article, section, nav, etc.)');
        }
        if (!geoIndicators.hasLlmSpecificMeta) {
            recommendations.push('Consider adding LLM-specific meta tags for optimization hints');
        }
        return {
            url,
            success: true,
            geoScore: Math.min(100, geoScore),
            geoIndicators,
            recommendations,
            summary: {
                isWellOptimized: geoScore >= 70,
                hasStructuredData: geoIndicators.hasJsonLd || geoIndicators.hasSchemaOrg,
                hasQAOptimization: geoIndicators.hasFAQSchema || geoIndicators.hasHowToSchema || geoIndicators.hasQAPageSchema,
                contentQuality: geoIndicators.hasClearHeadings && geoIndicators.wordCount >= 300,
                hasAuthoritySignals: geoIndicators.hasAuthorInfo || geoIndicators.hasDateInfo || geoIndicators.hasCitations
            },
            analyzedAt: new Date().toISOString()
        };
    }
    catch (error) {
        return {
            url,
            success: false,
            error: error.message || 'Failed to analyze GEO optimization',
            analyzedAt: new Date().toISOString()
        };
    }
}
(0, opal_tools_sdk_1.tool)({
    name: 'analyze-geo',
    description: 'Analyzes if a URL is optimized for Generative Engine Optimization (GEO) - optimization for LLMs like ChatGPT, Claude, etc.',
    parameters: [
        {
            name: 'url',
            type: opal_tools_sdk_1.ParameterType.String,
            description: 'The URL to analyze for GEO optimization',
            required: true
        }
    ]
})(analyzeGeoOptimization);
// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Discovery endpoint: http://localhost:${PORT}/discovery`);
});

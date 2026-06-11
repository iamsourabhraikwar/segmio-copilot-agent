import { NextRequest, NextResponse } from 'next/server';
import { MongoClient } from 'mongodb';
export const dynamic = 'force-dynamic';

// ============================================================
// MCP Server — Streamable HTTP Transport (2025-11-25 spec)
// Also maintains legacy SSE transport for the /agent demo page.
// GCP Agent Builder uses Streamable HTTP (POST-only).
// ============================================================

let cachedClient: MongoClient | null = null;

async function getMongoClient(): Promise<MongoClient> {
  if (cachedClient) return cachedClient;
  const mongoUri = process.env.MONGODB_URI;
  if (!mongoUri) throw new Error('MONGODB_URI not configured');
  const client = new MongoClient(mongoUri, { connectTimeoutMS: 5000, serverSelectionTimeoutMS: 5000 });
  await client.connect();
  cachedClient = client;
  return client;
}

async function queryMongodbInventory(query: string): Promise<any[] | null> {
  try {
    const client = await getMongoClient();
    const db = client.db('segmio_store');
    const collection = db.collection('products');
    const filter = {
      $or: [
        { name: { $regex: query, $options: 'i' } },
        { description: { $regex: query, $options: 'i' } },
        { category: { $regex: query, $options: 'i' } }
      ]
    };
    const results = await collection.find(filter).toArray();
    return results.map(doc => ({
      ...doc,
      _id: doc._id.toString()
    }));
  } catch (error) {
    console.error('[MCP MongoDB Connection Error]', error);
    return null;
  }
}

// Session storage for Streamable HTTP
const mcpSessions = new Map<string, { createdAt: number }>();

function generateSessionId(): string {
  return `mcp-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;
}

// Legacy SSE support for the /agent demo page
const activeClients = new Map<string, ReadableStreamDefaultController>();

const PRODUCTS_INVENTORY = [
  {
    name: 'AeroSound X200 Pro Headphones',
    description: 'Sleek wireless headphones with active noise cancellation, custom audio profiling, and 40-hour battery life. Perfect for audio engineering and daily commuting.',
    price: '$199.99',
    category: 'Electronics',
    imageUrl: '/images/products/aerosound_x200.png',
  },
  {
    name: 'LumiGlow Smart LED Lamp',
    description: 'A minimalist bedside lamp with smart app controls, scheduling, 16 million colors, and voice integration. Brighten your bedroom with custom ambient lighting.',
    price: '$49.99',
    category: 'Home Decor',
    imageUrl: '/images/products/lumiglow_lamp.png',
  },
  {
    name: 'FitTrack Elite Smartwatch',
    description: 'Robust fitness smartwatch with heart-rate tracking, sleep metrics, built-in GPS, and waterproof metal design. Track your goals with up to 14 days of battery life.',
    price: '$129.99',
    category: 'Wearables',
    imageUrl: '/images/products/fittrack_watch.png',
  },
  {
    name: 'Veloce Carbon Fiber Bicycle',
    description: 'Ultra-lightweight aerodynamic road bike with professional Shimano gears, carbon fiber frame, and puncture-resistant tyres. Engineered for peak racing performance.',
    price: '$1,499.00',
    category: 'Sports',
    imageUrl: '/images/products/veloce_bike.png',
  },
];

// MCP tool definitions — shared between initialize response and tools/list
const MCP_TOOLS = [
  {
    name: 'mongodb_mcp',
    description: 'Fuzzy search the Segmio store product database inventory. Returns product name, description, price, category, and image URL for matching products.',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'The search term, category, or product name to look up in the database.'
        }
      },
      required: ['query']
    }
  },
  {
    name: 'trigger_segmio_pipeline',
    description: 'Trigger sequential multi-scene AI video render on the Segmio platform. Each scene includes a script segment, visual prompt, and continuity flag.',
    inputSchema: {
      type: 'object',
      properties: {
        project_name: {
          type: 'string',
          description: 'The title of the video project.'
        },
        scenes: {
          type: 'array',
          description: 'Chronological list of video segments to render.',
          items: {
            type: 'object',
            properties: {
              scene_number: { type: 'integer' },
              script_segment: { type: 'string', description: 'The specific voiceover script segment.' },
              visual_prompt: { type: 'string', description: 'Visual prompts for video generation.' },
              use_last_frame_as_seed: { type: 'boolean', description: 'Visual continuity flag.' }
            },
            required: ['scene_number', 'script_segment', 'visual_prompt', 'use_last_frame_as_seed']
          }
        }
      },
      required: ['project_name', 'scenes']
    }
  }
];

// Handle tool execution
async function executeToolCall(toolName: string, toolArgs: Record<string, any>, request: NextRequest): Promise<any> {
  if (toolName === 'mongodb_mcp') {
    const query = (toolArgs.query || '').trim();
    console.log(`[MCP Server] Querying MongoDB Atlas for: "${query}"`);
    let matches = await queryMongodbInventory(query);
    if (matches === null) {
      console.warn('[MCP Server] MongoDB query failed. Falling back to static inventory.');
      const queryLower = query.toLowerCase();
      matches = PRODUCTS_INVENTORY.filter(p =>
        p.name.toLowerCase().includes(queryLower) ||
        p.description.toLowerCase().includes(queryLower) ||
        p.category.toLowerCase().includes(queryLower)
      );
    }
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(matches.length > 0 ? matches : [PRODUCTS_INVENTORY[0]])
        }
      ]
    };
  } else if (toolName === 'trigger_segmio_pipeline') {
    const host = request.headers.get('host') || 'segmio.ai';
    const protocol = request.headers.get('x-forwarded-proto') || 'https';
    
    // Use local loopback for any non-localhost/non-127.0.0.1 requests to bypass Cloudflare reverse proxy blocking
    const isLocal = host?.includes('localhost') || host?.includes('127.0.0.1');
    const renderEndpoint = isLocal 
      ? `${protocol}://${host}/api/hackathon/generate-video`
      : `http://127.0.0.1:${process.env.PORT || 3000}/api/hackathon/generate-video`;
      
    console.log(`[MCP Server] Forwarding trigger payload to (host: ${host}): ${renderEndpoint}`);
    const expectedApiKey = process.env.HACKATHON_SECRET_KEY || 'segmio-hackathon-2026-secret';
    
    // Add a 30-second abort timeout for the fetch call
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    
    try {
      const renderRes = await fetch(renderEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': expectedApiKey
        },
        body: JSON.stringify({
          title: toolArgs.project_name || 'Hackathon Video',
          continuity: true,
          scenes: toolArgs.scenes?.map((s: any) => ({
            text: s.script_segment,
            visual_prompt: s.visual_prompt,
            use_last_frame_as_seed: s.use_last_frame_as_seed
          }))
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      const renderData = await renderRes.json();
      if (!renderRes.ok) {
        throw new Error(renderData.error || `Failed to start video rendering (status: ${renderRes.status})`);
      }
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              message: 'Render pipeline successfully triggered!',
              videoId: renderData.videoId,
              scenesTriggered: renderData.scenes
            })
          }
        ]
      };
    } catch (fetchErr: any) {
      clearTimeout(timeoutId);
      console.error('[MCP Server] Error forwarding render payload:', fetchErr.message);
      throw fetchErr;
    }
  }
  return null;
}

// CORS preflight handler
export async function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Mcp-Session-Id, Accept',
      'Access-Control-Expose-Headers': 'Mcp-Session-Id',
    },
  });
}

// GET: Legacy SSE transport for the /agent demo page
export async function GET(request: NextRequest) {
  const sessionId = Math.random().toString(36).substring(2, 15);
  const host = request.headers.get('host') || 'localhost:3000';
  const protocol = request.headers.get('x-forwarded-proto') || 'http';

  console.log(`[MCP Server] Establishing SSE stream for session: ${sessionId}`);
  const stream = new ReadableStream({
    start(controller) {
      activeClients.set(sessionId, controller);
      const endpointUrl = `${protocol}://${host}/api/hackathon/mcp?sessionId=${sessionId}`;
      controller.enqueue(new TextEncoder().encode(`event: endpoint\ndata: ${endpointUrl}\n\n`));
      const interval = setInterval(() => {
        try {
          controller.enqueue(new TextEncoder().encode(': ping\n\n'));
        } catch {
          clearInterval(interval);
          activeClients.delete(sessionId);
        }
      }, 15000);

      request.signal.addEventListener('abort', () => {
        clearInterval(interval);
        activeClients.delete(sessionId);
        console.log(`[MCP Server] Session ${sessionId} aborted/closed.`);
      });
    },
    cancel() {
      activeClients.delete(sessionId);
    }
  });
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*',
    },
  });
}

// POST: Streamable HTTP transport (GCP Agent Builder) + legacy SSE POST
export async function POST(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const legacySessionId = searchParams.get('sessionId') || '';
    const body = await request.json();

    console.log(`[MCP Debug] Method: ${body.method}, ID: ${body.id}`);
    console.log(`[MCP Debug] Body:`, JSON.stringify(body, null, 2));

    const { jsonrpc, method, params, id } = body;

    if (jsonrpc !== '2.0' || !method) {
      return NextResponse.json({
        jsonrpc: '2.0',
        error: { code: -32600, message: 'Invalid Request' },
        id: id || null
      }, {
        status: 400,
        headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Expose-Headers': 'Mcp-Session-Id' }
      });
    }

    // Determine or create session
    let sessionId = request.headers.get('mcp-session-id') || '';
    const responseHeaders: Record<string, string> = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Expose-Headers': 'Mcp-Session-Id',
    };

    let responseResult: any = null;

    // ---- MCP Protocol Methods ----

    if (method === 'initialize') {
      // Streamable HTTP: create a new session
      sessionId = generateSessionId();
      mcpSessions.set(sessionId, { createdAt: Date.now() });
      responseHeaders['Mcp-Session-Id'] = sessionId;
      console.log(`[MCP Server] Initialize — new session: ${sessionId}`);

      responseResult = {
        protocolVersion: '2025-03-26',
        capabilities: {
          tools: { listChanged: false },
        },
        serverInfo: {
          name: 'Segmio Product Database',
          version: '1.0.0',
        },
      };
    } else if (method === 'notifications/initialized') {
      // Client acknowledgement — no response needed, return 200
      if (sessionId) responseHeaders['Mcp-Session-Id'] = sessionId;
      return NextResponse.json({
        jsonrpc: '2.0',
        result: {},
        id
      }, { headers: responseHeaders });
    } else if (method === 'tools/list') {
      if (sessionId) responseHeaders['Mcp-Session-Id'] = sessionId;
      responseResult = { tools: MCP_TOOLS };
    } else if (method === 'tools/call') {
      if (sessionId) responseHeaders['Mcp-Session-Id'] = sessionId;
      const toolName = params?.name;
      const toolArgs = params?.arguments || {};

      const result = await executeToolCall(toolName, toolArgs, request);
      if (result === null) {
        return NextResponse.json({
          jsonrpc: '2.0',
          error: { code: -32601, message: `Tool not found: ${toolName}` },
          id
        }, { status: 404, headers: responseHeaders });
      }
      responseResult = result;
    } else if (method === 'ping') {
      if (sessionId) responseHeaders['Mcp-Session-Id'] = sessionId;
      responseResult = {};
    } else {
      // Unknown method
      if (sessionId) responseHeaders['Mcp-Session-Id'] = sessionId;
      responseResult = {};
    }

    const responsePayload = {
      jsonrpc: '2.0' as const,
      result: responseResult,
      id
    };

    // Legacy SSE: also push to SSE stream if active
    const sseController = activeClients.get(legacySessionId);
    if (sseController) {
      try {
        sseController.enqueue(new TextEncoder().encode(`event: message\ndata: ${JSON.stringify(responsePayload)}\n\n`));
      } catch (err) {
        console.warn('[MCP Server] Failed to enqueue to SSE client:', err);
      }
    }

    return NextResponse.json(responsePayload, { headers: responseHeaders });
  } catch (error: any) {
    console.error('[MCP Server Error]', error);
    return NextResponse.json({
      jsonrpc: '2.0',
      error: { code: -32603, message: error.message || 'Internal error' },
      id: null
    }, {
      status: 500,
      headers: { 'Access-Control-Allow-Origin': '*' }
    });
  }
}

// DELETE: Session termination (Streamable HTTP spec)
export async function DELETE(request: NextRequest) {
  const sessionId = request.headers.get('mcp-session-id') || '';
  if (sessionId && mcpSessions.has(sessionId)) {
    mcpSessions.delete(sessionId);
    console.log(`[MCP Server] Session terminated: ${sessionId}`);
  }
  return new Response(null, {
    status: 204,
    headers: { 'Access-Control-Allow-Origin': '*' },
  });
}

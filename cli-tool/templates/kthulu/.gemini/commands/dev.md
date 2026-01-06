---
description: Start Kthulu Full Stack (Backend + Frontend)
---

# Start Backend (Background)

echo "🚀 Starting Go Backend..."
if [ -f "main.go" ]; then
go run main.go &
BACKEND_PID=$!
elif [ -d "cmd/server" ]; then
    go run cmd/server/main.go &
    BACKEND_PID=$!
else
echo "⚠️ Could not find main.go entry point."
fi

# Start Frontend

echo "🎨 Starting Frontend..."
if [ -d "frontend" ]; then
cd frontend
npm run dev
else
echo "⚠️ Frontend directory not found."
fi

# Cleanup

if [ -n "$BACKEND_PID" ]; then
kill $BACKEND_PID
fi

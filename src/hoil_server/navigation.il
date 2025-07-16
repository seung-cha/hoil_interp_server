

forwardSpeed is 0.3
turnSpeed is 0.3

forwardThreshold is 0.7
leftThreshold is 0.7
rightThreshold is 0.7

moveForwardMode is true
turnRightMode is false


repeat until true
{
    >> "If set to go forward"
    {
        call Print("Moving Forward")

        # 1. Move forwards til there is an obstacle
        # 2. If there is, stop moving and start turning to avoid obstacle
        >> "Move forward"

        >> "If the obstacle ahead is too close"
        {
            call Print("Enabling Turning Mode")
            >> "Stop moving forward"
            >> "Disable moving forward mode"
            >> "Enable turn mode"
        }
    }
    

    >> "If set to turn"
    {
        call Print("Turning Right")
        >> "Turn right"
        >> "If the obstacle to the robot's left is not too close"
        {
            call Print("Enabling Turning Mode")
            # Disable turning mode and start moving again
            >> "Stop turning"
            >> "Enable moving mode"
            >> "Disable turning mode"
        }
    }

    >> "Wait 0.1 seconds"
}
